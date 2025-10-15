from fastapi import HTTPException, Response, status, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=['Posts'])

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor(row_factory=dict_row) as cursor:
    #         cursor.execute("SELECT * FROM posts")
    #         posts = cursor.fetchall()    
    print(limit)
    posts = db.query(models.Post, func.count(models.Vote.user_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user:models.User = Depends(oauth2.get_current_user)):
    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    #         post_new = cursor.fetchone()
    #         conn.commit()
    print(current_user.email)
    post_new = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(post_new)
    db.commit()
    db.refresh(post_new)
    return post_new

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor(row_factory=dict_row) as cursor:
    #         cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    #         post = cursor.fetchone()
    post = db.query(models.Post, func.count(models.Vote.user_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")

    return post

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    # with psycopg.connect(**DB_CONFIG) as conn:
    #     with conn.cursor(row_factory=dict_row) as cursor:
    #         cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    #         post = cursor.fetchone()
    #         conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorised for requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        requested_post_query = db.query(models.Post).filter(models.Post.id == id)
        requested_post = requested_post_query.first()
        if not requested_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")
        
        if requested_post.owner_id != current_user.id:
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorised for requested action")

        requested_post_query.update(updated_post.model_dump(), synchronize_session=False)
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