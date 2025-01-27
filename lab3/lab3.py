from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

BASE_URL = "https://jsonplaceholder.typicode.com"

# Fetch posts for a specific userID
async def fetch_user_posts(userID: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/posts", params={"userId": userID})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching posts")
        return response.json()

# Fetch comments for a specific postID
async def fetch_post_comments(postID: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/comments", params={"postId": postID})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching comments")
        return response.json()

@app.get("/detailed_post/{userID}")
async def get_detailed_post(userID: int):
    posts = await fetch_user_posts(userID)
    detailed_posts = []
    
    for post in posts:
        post_id = post['id']
        comments = await fetch_post_comments(post_id)
        detailed_post = {
            "post_title": post['title'],
            "post_body": post['body'],
            "comments": comments
        }
        detailed_posts.append(detailed_post)

    return {
        "userID": userID,
        "posts": detailed_posts
    }
