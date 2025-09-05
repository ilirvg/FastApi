from fastapi import HTTPException, Response, status, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favorite foods", "content": "I like pizza", "id": 2}
    ]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@router.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor(row_factory=dict_row) as cursor:
    #         cursor.execute("SELECT * FROM posts")
    #         posts = cursor.fetchall()    
    posts = db.query(models.Post).all()
    return posts

@router.post("/createpost", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    #         post_new = cursor.fetchone()
    #         conn.commit()
    post_new = models.Post(**post.model_dump())
    db.add(post_new)
    db.commit()
    db.refresh(post_new)
    return post_new

@router.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor(row_factory=dict_row) as cursor:
    #         cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    #         post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")

    return post

@router.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor(row_factory=dict_row) as cursor:
    #         cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    #         post = cursor.fetchone()
    #         conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/posts/{id}', response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Starting update for post {id}")

        requested_post = db.query(models.Post).filter(models.Post.id == id)
        logger.info("Query created")

        if not requested_post.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")
        
        logger.info("Post found, updating...")

        requested_post.update(updated_post.model_dump(), synchronize_session=False)
        db.commit()

        # Get the updated post to return
        updated_record = db.query(models.Post).filter(models.Post.id == id).first()

        return updated_record
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error updating post {id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}") 