from sqlalchemy import select
import pandas as pd
import datetime
from pathlib import Path
from app.db.database import get_db
from app.model.paper import Paper

def seed_paper_from_csv(db):
    csv_path = Path(__file__).parent.parent / 'ml' / 'arxiv_recap.csv'
    df = pd.read_csv(csv_path)
    
    for _,row in df.iterrows():
        paper = Paper(
            title=row["title"],
            abstract=row["abstract"],
            published_date = row['published_date'],
            category = row['category'],
            url = row['url'],
            author=row['authors']
        )
        db.add(paper)
    db.commit()
    print("Seeding selesai ✅")

if __name__ == "__main__":
    db = next(get_db())
    try:
        seed_paper_from_csv(db)
    finally:
        db.close()