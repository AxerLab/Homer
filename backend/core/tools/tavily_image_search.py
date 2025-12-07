"""
Tavily Image Search Tool for Pydantic AI Agent.

This module provides a tool for searching images using the Tavily Search API.
"""

import os
from typing import Literal
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def tavily_image_search(
    query: str,
    count: int = 5,
    search_depth: Literal["basic", "advanced"] = "basic",
) -> str:
    """
    Search for images on the web using Tavily Search API.
    
    Use this tool when you need to find images related to a topic for presentations,
    visual references, or when the user asks for image suggestions.
    
    Args:
        query: The search query for finding images. Be specific and descriptive.
        count: Number of image results to return (1-20, default 5).
        search_depth: Search depth - "basic" (faster) or "advanced" (more thorough).
    
    Returns:
        A formatted string containing image search results with URLs and metadata.
    """
    if not TAVILY_API_KEY:
        return "Error: TAVILY_API_KEY environment variable is not set. Please configure your Tavily Search API key."
    
    # Clamp count to reasonable limits
    count = max(1, min(count, 20))
    
    try:
        # Initialize Tavily client
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        # Perform search with include_images=True
        response = client.search(
            query=query,
            max_results=count,
            include_images=True,
            search_depth=search_depth,
            include_answer=False,  # We don't need text answers for image search
        )
        
        # Extract images from response
        images = response.get("images", [])
        results = response.get("results", [])
        
        if not images and not results:
            return f"No images found for query: '{query}'"
        
        # Format results for the agent
        formatted_results = []
        
        # Primary images from the images field
        if images:
            formatted_results.append("**Image URLs:**")
            for i, image_url in enumerate(images[:count], 1):
                formatted_results.append(f"{i}. {image_url}")
        
        # Additional context from search results
        if results and len(results) > 0:
            formatted_results.append("\n**Image Sources:**")
            for i, result in enumerate(results[:min(3, len(results))], 1):
                title = result.get("title", "Untitled")
                url = result.get("url", "N/A")
                formatted_results.append(
                    f"{i}. **{title}**\n"
                    f"   - Source URL: {url}"
                )
        
        original_query = response.get("query", query)
        header = f"Image Search Results for: '{original_query}'\n"
        header += f"Found {len(images)} image(s)\n"
        
        return header + "\n" + "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching for images: {str(e)}"


def tavily_image_search_tool(max_results: int = 5):
    """
    Factory function to create a Tavily image search tool with configurable max results.
    
    Args:
        max_results: Maximum number of results to return (default 5, max 20).
    
    Returns:
        An async function suitable for use as a Pydantic AI tool.
    """
    max_results = max(1, min(max_results, 20))
    
    async def _search(
        query: str,
        count: int = max_results,
        search_depth: Literal["basic", "advanced"] = "basic",
    ) -> str:
        """
        Search for images on the web using Tavily Search API.
        
        Use this tool to find relevant images for presentations, slides, or visual content.
        Returns image URLs and source metadata.
        
        Args:
            query: The search query for finding images. Be specific and descriptive 
                   (e.g., "mountain landscape sunset" instead of just "mountain").
            count: Number of results to return (1-{max_results}, default {max_results}).
            search_depth: Search depth - "basic" (faster, default) or "advanced" (more thorough).
        
        Returns:
            Formatted image search results including image URLs and source information.
        """
        return await tavily_image_search(
            query=query,
            count=min(count, max_results),
            search_depth=search_depth,
        )
    
    # Update docstring with actual max_results value
    if _search.__doc__:
        _search.__doc__ = _search.__doc__.format(max_results=max_results)
    _search.__name__ = "tavily_image_search"
    
    return _search
