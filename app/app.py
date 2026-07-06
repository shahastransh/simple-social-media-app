from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from app.schema import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, get_async_session, create_db_and_tables, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import os
import shutil
import uuid
import tempfile
from app.user import current_active_user, auth_backend, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"]
)


@app.post("/upload")
async def upload_file(
    file : UploadFile = File(...),
    caption : str = Form(""),
    user: User = Depends(current_active_user),
    session : AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try: 
        # 1. Safely handle the filename just in case it comes in as None
        safe_filename = file.filename if file.filename else "default_upload"
        file_suffix = os.path.splitext(safe_filename)[1]

        # 2. Save the upload to a temp file using the safe suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        # 3. Open the file properly so it closes before os.unlink tries to delete it
        with open(temp_file_path, "rb") as image_file_to_upload:
            upload_result = imagekit.files.upload(
                file=image_file_to_upload,
                file_name=safe_filename,  # Use the safe filename here too
                use_unique_file_name=True,
                tags=["backend-upload"]
            )

        # 4. Save to database if the upload has a URL (NEW CHECK HERE)
        if hasattr(upload_result, 'url') and upload_result.url:
            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_result.url, 
                file_type="video" if file.content_type and file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve URL from ImageKit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

@app.get("/feed")
async def get_feed(session : AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []

    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "isOwner": post.user_id == user.id,  # Check if the current user is the owner of the post
                "email": user_dict.get(post.user_id, "Unknown User")  # Include the email of the current user
            }
        )

    return {"posts" : posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        # Convert the string to a UUID
        post_uuid = uuid.UUID(post_id)

        # Execute the query
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        
        # Safely fetch the single post or return None
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        # Delete and commit
        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message": f"Post with id {post_id} deleted successfully."}
        
    except ValueError:
        # Catches cases where post_id is not a properly formatted UUID string
        raise HTTPException(status_code=400, detail="Invalid post ID format.")
    except Exception as e:
        # Notice the capital 'E' in Exception
        raise HTTPException(status_code=500, detail=str(e))

    
    















































































# @app.get("/hello-world")
# def hello_world():
#     return {"message":"Hello,World!"} #JSON javascript object notation

# text_posts = {1 : {"title" : "New Post", "content" : "cool test post"},
#               2 : {"title": "New Post", "content": "Cool test post"},
#    3 : {"title": "Python Tip", "content": "Use list comprehensions for cleaner loops."},
#     4 : {"title": "Daily Motivation", "content": "Consistency beats intensity every time."},
#     5 : {"title": "Fun Fact", "content": "The first computer bug was an actual moth found in a Harvard Mark II."},
#     6 : {"title": "Update", "content": "Just launched my new project! Excited to share more soon."},
#     7 : {"title": "Tech Insight", "content": "Async IO in Python can massively speed up I/O-bound tasks."},
#     8 : {"title": "Quote", "content": "Programs must be written for people to read, and only incidentally for machines to execute."},
#     9 : {"title": "Weekend Plans", "content": "Might finally clean up my GitHub repos... or just play some Minecraft"},
#     10 : {"title": "Question", "content": "What's the most underrated Python library you've ever used?"},
#     11 : {"title": "Mini Announcement", "content": "New video drops tomorrow-covering the weirdest Python features!"}}

# @app.get("/posts")
# def get_all_posts(limit : int = None):
#     if limit :
#         return list(text_posts.values())[:limit]
#     return text_posts

# @app.get("/posts/{id}") 
# def get_post(id : int) -> PostResponse:
#     if id not in text_posts:
#         raise HTTPException(status_code = 404, detail = f'Post with id {id} not found')
#     return text_posts.get(id)

# @app.post("/posts")
# def create_post(post : PostCreate) -> PostResponse:
#     new_post = {"title" : post.title, "content" : post.content}
#     text_posts[max(text_posts.keys()) + 1] = new_post
#     return new_post 
