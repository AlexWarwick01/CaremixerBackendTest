# External API integration module
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import httpx
import asyncio

router = APIRouter()

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/"

# Defining the Pydantic model for the external data
class Pokemon(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    types: List[str]
    image_url: Optional[str] = None

class PokemonResponse(BaseModel):
    pokemon: List[Pokemon]
    page: int
    total: int
    has_more: bool

POKEMON_CACHE = {} # Simple in-memory cache


async def fetch_pokemon_details(name: str) -> Optional[Pokemon]:

    # First Check the Cache
    if name.lower() in POKEMON_CACHE:
        print(f"Cache hit for {name}")
        return POKEMON_CACHE[name.lower()]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{POKEMON_API_URL}{name.lower()}")

            if response.status_code == 200:
                data = response.json()
                
                # Safely extract image URL
                image_url = None
                try:
                    image_url = data["sprites"]["other"]["official-artwork"]["front_default"]
                except (KeyError, TypeError):
                    pass
                
                pokemon = Pokemon(
                    id=data['id'],
                    name=data['name'],
                    height=data['height'],
                    weight=data['weight'],
                    types=[t["type"]["name"] for t in data["types"]],
                    image_url=image_url
                )

                POKEMON_CACHE[name.lower()] = pokemon # Cache the result
                return pokemon 
            else:
                return None
    except (httpx.TimeoutException, httpx.RequestError) as e:
        # Handle Network Errors
        print(f"Error fetching data for {name}: {str(e)}")
        return None

@router.get("/", response_model=PokemonResponse)
async def get_pokemon_data(
    page: int = Query(1, ge=1, description="Page number for pagination"), 
    limit: int = Query(10, ge=1, le=50, description="Number of items per page (max 50)"),
    search: Optional[str] = Query(None, description="Search term for Pokemon name")
):
# This endpoint fetches Pokemon data from the external API with pagination and optional search
# Example: /external_data/?page=2&limit=5&search=pikachu - fetches page 2 with 5 items per page, filtering names containing "pikachu"
# Example: /external_data/?page=1&limit=10 - will return the first 10 Pokemon
# Example: /external_data/?search=char - will return all Pokemon with "char" in their name

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # If searching, fetch a larger set to search through (up to 1000 pokemon)
            if search:
                # Fetch more results to search through
                response = await client.get(POKEMON_API_URL, params={"offset": 0, "limit": 1000})
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from external API")
                
                data = response.json()
                results = data["results"]
                
                # Filter by search term
                results = [item for item in results if search.lower() in item["name"].lower()]
                
                # Apply pagination to filtered results
                offset = (page - 1) * limit
                total_filtered = len(results)
                results = results[offset:offset + limit]
                
                # Fetch detailed data for each Pokemon concurrently
                tasks = [fetch_pokemon_details(item["name"]) for item in results]
                pokemons = await asyncio.gather(*tasks)
                
                # Filter out None results (failed fetches)
                pokemons = [p for p in pokemons if p is not None]
                
                has_more = (offset + limit) < total_filtered
                
                return PokemonResponse(
                    pokemon=pokemons,
                    page=page,
                    total=total_filtered,
                    has_more=has_more
                )
            else:
                # Normal pagination without search
                offset = (page - 1) * limit
                response = await client.get(POKEMON_API_URL, params={"offset": offset, "limit": limit})

                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from external API")

                data = response.json()
                results = data["results"]
                total = data["count"]

                # Fetch detailed data for each Pokemon concurrently
                tasks = [fetch_pokemon_details(item["name"]) for item in results]
                pokemons = await asyncio.gather(*tasks)

                # Filter out None results (failed fetches)
                pokemons = [p for p in pokemons if p is not None]

                has_more = (offset + limit) < total

                return PokemonResponse(
                    pokemon=pokemons,
                    page=page,
                    total=total,
                    has_more=has_more
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@router.get("/{pokemon_name}", response_model=Pokemon)
async def get_pokemon_by_name(pokemon_name: str):
    # This endpoint fetches detailed data for a specific Pokemon by name
    pokemon = await fetch_pokemon_details(pokemon_name)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return pokemon
