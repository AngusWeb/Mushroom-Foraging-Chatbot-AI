import asyncio
import requests
import json
import os
from twikit.client.client import Client
from typing import NoReturn

async def main() -> NoReturn:
  
    client = Client(language='en-US')
    
    #Path to the cookies file
    cookies_file = 'cookies.json'
    username = ''
    # Check if cookies file exists
    if os.path.exists(cookies_file):
        # Load cookies from the file
        client.load_cookies(cookies_file)
        print("Loaded cookies from file.")
    else:
         
             # Replace with your Twitter username 
        password = '' 
        EMAIL = ''# Replace with your Twitter password'
        print("Logged in with username and password.")
        
        print("Saved cookies to file.")
        # Log in to Twitter account
        await client.login(
            auth_info_1=username,
            auth_info_2=EMAIL,
            password=password,
        )
        client.save_cookies(cookies_file)
    # Initialize the set to keep track of replied tweet IDs
    replied_tweet_ids = set()
    if False:
        test_tweet = await client.create_tweet(text="third tweet")
        print("Test tweet posted:", test_tweet)
    await client.create_tweet(text="first reply",reply_to='1858550582300254374')
    # Function to get the latest tweets mentioning you
    async def get_latest_mentions():
        query = f'@{username} -from:{username}'
        return await client.search_tweet(query=query, product='Latest', count=20)

    # Get the initial set of tweets to establish a baseline
    previous_tweets = await get_latest_mentions()

    # Add their IDs to the set to prevent immediate replies
    for tweet in previous_tweets:
        replied_tweet_ids.add(tweet.id)

    while True:
        await asyncio.sleep(60)  # Wait for 1 minute
        latest_tweets = await get_latest_mentions()

        for tweet in latest_tweets:
            # Check if we have already replied to this tweet
            if tweet.id not in replied_tweet_ids:
                # Extract the tweet text
                tweet_text = tweet.text
                tweet_text = tweet_text[16:]
                print(f"tweet found:{tweet_text}")
                # Formulate the prompt for the LLM
                prompt = f"Reply to this tweet in no more than 250 characters: {tweet_text}"

                # Get the response from Ollama
                response_text = get_llm_response(prompt)
                print(f"model response:{response_text}")
                # Reply to the tweet with the generated response
                #await tweet.reply(text=response_text)
                await tweet.create_tweet(text=response_text,reply_to=tweet.id)
                # Add the tweet ID to the set of replied tweets
                replied_tweet_ids.add(tweet.id)

                # Print a log message
                print(f"Replied to tweet ID {tweet.id} with text: {response_text}")

        
        if len(replied_tweet_ids) > 1000:
            replied_tweet_ids = set(list(replied_tweet_ids)[-500:])

def get_llm_response(prompt):


    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": "v1_mushroom",  # model's name in Ollama
        "prompt": prompt,
        "stream": True,          # streaming response
    }
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        if response.status_code == 200:
            # Read the response stream and concatenate the outputs
            generated_text = ''
            buffer = ''
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                buffer += chunk.decode('utf-8')
                # Process buffer for complete JSON objects
                lines = buffer.split('\n')
                # Keep the last partial line in the buffer
                buffer = lines.pop()
                for line in lines:
                    if line.strip() == '':
                        continue
                    try:
                        json_obj = json.loads(line)
                        # Extract the 'response' field
                        response_text = json_obj.get('response', '')
                        generated_text += response_text
                    except json.JSONDecodeError:
                        # Skip lines that can't be parsed
                        continue
            
            if buffer.strip():
                try:
                    json_obj = json.loads(buffer)
                    response_text = json_obj.get('response', '')
                    generated_text += response_text
                except json.JSONDecodeError:
                    pass  
            return generated_text.strip()
        else:
            print(f"Error fetching from Ollama API: {response.status_code}")
            return "Sorry, I'm unable to process your request at the moment."
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return "Sorry, I'm unable to process your request at the moment."

if __name__ == '__main__':

    asyncio.run(main())
