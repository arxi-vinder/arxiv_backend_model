import os
import sys
import logging
import click
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.repositories.paper_repository import PaperRepository
from app.services.recommendation_service import RecommendationService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@click.group()
def cli():
    """Arxivinder Vectorization CLI Tool"""
    pass


@cli.command()
@click.option('--batch-size', default=100, help='Batch size for processing papers (default: 100)')
@click.option('--force', is_flag=True, help='Force vectorization even if cache exists')
def vectorize_all(batch_size, force):
    """Vectorize all papers in the database"""
    try:
        click.echo("\n" + "="*60)
        click.echo("[START] Starting Paper Vectorization Process")
        click.echo("="*60)

        # Initialize database session
        db = SessionLocal()
        try:
            paper_repo = PaperRepository(db) # type: ignore

            # Check total papers
            total_papers = paper_repo.get_total_papers_count()
            click.echo(f"\n[INFO] Total papers in database: {total_papers}")

            if total_papers == 0:
                click.secho("[WARN] No papers found in database!", fg="yellow")
                return

            # Initialize recommendation service
            rec_service = RecommendationService(
                paper_repository=paper_repo,
                auto_build=False,
                use_cache=True
            )

            # Check if cache exists and ask if not forcing
            cache_info = rec_service.cache_service.get_cache_info()
            if cache_info.get("status") == "cached" and not force:
                click.secho(f"\n[CACHE] Cache already exists:", fg="cyan")
                click.echo(f"   - Papers cached: {cache_info.get('total_papers')}")
                click.echo(f"   - Cache file size: {cache_info.get('file_size_mb')} MB")
                click.echo(f"   - Last updated: {cache_info.get('saved_at')}")

                if click.confirm("\n[ASK] Do you want to re-vectorize anyway?", default=False):
                    click.echo("[OK] Proceeding with re-vectorization...")
                else:
                    click.secho("[SKIP] Skipped vectorization", fg="yellow")
                    return

            # Start vectorization
            click.echo(f"\n[RUN] Starting vectorization with batch size: {batch_size}...")
            click.echo("-" * 60)

            rec_service.build_full_model_batch(batch_size=batch_size, verbose=True)

            click.echo("-" * 60)
            click.secho("\n[DONE] Vectorization completed successfully!", fg="green")

            # Show final cache info
            final_cache_info = rec_service.cache_service.get_cache_info()
            if final_cache_info.get("status") == "cached":
                click.secho("\n[STATS] Final Cache Status:", fg="cyan")
                click.echo(f"   - Total papers: {final_cache_info.get('total_papers')}")
                click.echo(f"   - Matrix size: {final_cache_info.get('matrix_size')}x{final_cache_info.get('matrix_size')}")
                click.echo(f"   - File size: {final_cache_info.get('file_size_mb')} MB")
                click.echo(f"   - Location: {final_cache_info.get('cache_file')}")

        finally:
            db.close()

    except Exception as e:
        click.secho(f"\n[ERROR] Error during vectorization: {str(e)}", fg="red")
        logger.error(f"Vectorization error: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
def cache_info():
    """Show cache information"""
    try:
        db = SessionLocal()
        try:
            paper_repo = PaperRepository(db) # type: ignore
            rec_service = RecommendationService(
                paper_repository=paper_repo,
                auto_build=False,
                use_cache=True
            )

            cache_info = rec_service.cache_service.get_cache_info()

            click.echo("\n" + "="*60)
            click.echo("[CACHE] Cache Information")
            click.echo("="*60)

            if cache_info.get("status") == "no_cache":
                click.secho("No cache found. Run 'python -m app.cli vectorize-all' to create cache.", fg="yellow")
            elif cache_info.get("status") == "error":
                click.secho(f"Error: {cache_info.get('message')}", fg="red")
            else:
                click.secho("[OK] Cache Status: CACHED", fg="green")
                click.echo(f"  - Total papers: {cache_info.get('total_papers')}")
                click.echo(f"  - Matrix size: {cache_info.get('matrix_size')}x{cache_info.get('matrix_size')}")
                click.echo(f"  - File size: {cache_info.get('file_size_mb')} MB")
                click.echo(f"  - Last saved: {cache_info.get('saved_at')}")
                click.echo(f"  - Cache location: {cache_info.get('cache_file')}")

        finally:
            db.close()

    except Exception as e:
        click.secho(f"[ERROR] Error: {str(e)}", fg="red")
        logger.error(f"Cache info error: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.confirmation_option(
    prompt='Are you sure you want to clear the cache? This cannot be undone.',
    default=False
)
def clear_cache():
    """Clear the vectorization cache"""
    try:
        db = SessionLocal()
        try:
            paper_repo = PaperRepository(db) # type: ignore
            rec_service = RecommendationService(
                paper_repository=paper_repo,
                auto_build=False,
                use_cache=True
            )

            success = rec_service.cache_service.clear_cache()
            if success:
                click.secho("[DONE] Cache cleared successfully!", fg="green")
            else:
                click.secho("[ERROR] Failed to clear cache", fg="red")
                sys.exit(1)

        finally:
            db.close()

    except Exception as e:
        click.secho(f"[ERROR] Error: {str(e)}", fg="red")
        logger.error(f"Clear cache error: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
def status():
    """Show vectorization status"""
    try:
        db = SessionLocal()
        try:
            paper_repo = PaperRepository(db) # type: ignore
            total_papers = paper_repo.get_total_papers_count()

            rec_service = RecommendationService(
                paper_repository=paper_repo,
                auto_build=False,
                use_cache=True
            )

            cache_info = rec_service.cache_service.get_cache_info()

            click.echo("\n" + "="*60)
            click.echo("[STATUS] Vectorization Status")
            click.echo("="*60)

            click.echo(f"\n[DB] Database:")
            click.echo(f"   - Total papers: {total_papers}")

            click.echo(f"\n[CACHE] Cache:")
            if cache_info.get("status") == "no_cache":
                click.secho("   Status: NOT CACHED", fg="yellow")
            elif cache_info.get("status") == "error":
                click.secho(f"   Status: ERROR - {cache_info.get('message')}", fg="red")
            else:
                click.secho("   Status: CACHED [OK]", fg="green")
                click.echo(f"   - Papers cached: {cache_info.get('total_papers')}")
                click.echo(f"   - Matrix size: {cache_info.get('matrix_size')}x{cache_info.get('matrix_size')}")
                click.echo(f"   - File size: {cache_info.get('file_size_mb')} MB")
                click.echo(f"   - Last updated: {cache_info.get('saved_at')}")

            click.echo("\n" + "="*60)

        finally:
            db.close()

    except Exception as e:
        click.secho(f"[ERROR] Error: {str(e)}", fg="red")
        logger.error(f"Status check error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
