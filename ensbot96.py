import tweepy
import requests
import time
import os
import random
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Authenticate Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# ENS Graph API URL
ENS_GRAPH_API = "https://api.thegraph.com/subgraphs/name/ensdomains/ens"

# Function to fetch ENS domain details
def fetch_ens_details(domain_name):
    query = f"""
    {{
        domains(where:{{name:"{domain_name}"}}) {{
            name
            owner {{
                id
            }}
            createdAt
            resolvedAddress {{
                id
            }}
        }}
    }}
    """
    response = requests.post(ENS_GRAPH_API, json={"query": query})
    data = response.json()

    if "data" in data and data["data"]["domains"]:
        domain_info = data["data"]["domains"][0]
        return f"🔹 Domain: {domain_info['name']}\n👤 Owner: {domain_info['owner']['id']}\n📅 Created: {domain_info['createdAt']}\n🔗 Address: {domain_info.get('resolvedAddress', {}).get('id', 'N/A')}"
    return "❌ ENS domain not found."

# Function to get AI ENS appraisal
def appraise_ens(domain_name):
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": f"Appraise the ENS domain: {domain_name} in a logical, engaging, and slightly humorous way."}

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return "❌ Unable to generate appraisal."

# Function to fetch latest ENS sales & registrations
def fetch_latest_ens_news():
    query = """
    {
      registrations(first: 3, orderBy: registrationDate, orderDirection: desc) {
        domain {
          name
        }
        registrant {
          id
        }
        registrationDate
      }
      wrappedDomains(first: 3, orderBy: expiryDate, orderDirection: desc) {
        domain {
          name
        }
        expiryDate
      }
    }
    """
    response = requests.post(ENS_GRAPH_API, json={"query": query})
    data = response.json()

    if "data" in data:
        news = "**🔥 Latest ENS News:**\n"
        if data["data"]["registrations"]:
            news += "\n🆕 **Recently Registered ENS Domains:**\n"
            for reg in data["data"]["registrations"]:
                news += f"• {reg['domain']['name']} (by {reg['registrant']['id']})\n"
        
        if data["data"]["wrappedDomains"]:
            news += "\n⏳ **Expiring Soon:**\n"
            for wrap in data["data"]["wrappedDomains"]:
                news += f"• {wrap['domain']['name']} (expires: {wrap['expiryDate']})\n"

        return news
    return "❌ Unable to fetch ENS news."

# Function to generate a humorous ENS opinion
def get_ens_opinion():
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": "Give a humorous and engaging opinion about the latest ENS domain trends."}

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return "❌ No ENS opinion available."

# Function to check Twitter mentions and reply using Free API workaround
def check_mentions():
    print("🔍 Checking Twitter mentions...")
    search_url = "https://api.twitter.com/2/tweets/search/recent?query=@ensbot96"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    response = requests.get(search_url, headers=headers)
    tweets = response.json()

    if "data" in tweets:
        for tweet in tweets["data"]:
            tweet_id = tweet["id"]
            user = tweet["author_id"]
            text = tweet["text"].lower()

            words = text.split()
            ens_domain = next((word for word in words if word.endswith(".eth")), None)

            if ens_domain:
                print(f"🛠 Processing {ens_domain} for user ID {user}...")

                # Fetch ENS data
                ens_data = fetch_ens_details(ens_domain)

                # Get AI appraisal
                appraisal = appraise_ens(ens_domain)

                # Reply to the tweet
                reply = f"🔥 ENS Domain Appraisal 🔥\n{ens_data}\n\n💰 AI Estimated Value:\n{appraisal}"
                api.update_status(status=reply, in_reply_to_status_id=tweet_id)
                print(f"✅ Replied to tweet ID {tweet_id}")

# Function to automatically post ENS news & opinion
def auto_post_ens_updates():
    news = fetch_latest_ens_news()
    opinion = get_ens_opinion()
    post = f"🚀 **ENS Market Update!**\n\n{news}\n\n💭 My Take: {opinion}"
    
    api.update_status(post)
    print("✅ Auto-posted ENS update!")

# Run bot continuously
while True:
    try:
        check_mentions()
        
        # Randomly post ENS updates every 3-6 hours
        if random.randint(1, 6) == 3:
            auto_post_ens_updates()
        
        time.sleep(60)  # Check mentions every minute
    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(60)
