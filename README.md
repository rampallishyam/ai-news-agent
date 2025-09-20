# 🤖 AI News Agent

An automated GitHub Actions-powered agent that collects, analyzes, and summarizes the latest AI news daily, then updates your Notion page with a professionally formatted brief.

## 🌟 Features

- **📰 Automated News Collection**: Scrapes multiple AI news RSS feeds
- **🧠 AI-Powered Analysis**: Uses Anthropic's Claude to generate intelligent summaries
- **📝 Notion Integration**: Automatically updates your Notion page with formatted content
- **⏰ Daily Scheduling**: Runs automatically every day via GitHub Actions
- **🔍 Smart Filtering**: Focuses on AI-relevant news with keyword filtering
- **🛡️ Error Handling**: Robust error handling with fallback mechanisms
- **💾 Backup System**: Creates backups before updating content
- **📊 Debug Mode**: Saves debug data for troubleshooting

## 🚀 Quick Setup

### 1. Set Up API Keys

#### Anthropic Claude API
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and generate an API key
3. Note: This is a paid service (~$1-3/month for daily summaries)

#### Notion API
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "AI News Agent")
4. Copy the integration token
5. Share your target page with this integration

#### Get Your Notion Page ID
From your page URL: `https://www.notion.so/workspace/Page-Title-{PAGE_ID}`
The page ID is the long string after the last dash.

### 2. Configure GitHub Secrets

In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**, then add:

- `ANTHROPIC_API_KEY`: Your Claude API key
- `NOTION_TOKEN`: Your Notion integration token  
- `NOTION_PAGE_ID`: Your target Notion page ID

### 3. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will run automatically at 8 AM UTC daily
4. For immediate testing, click **Run workflow** manually

## 🛠️ Configuration

### News Sources

The agent monitors these AI news sources by default:

- **TechCrunch AI** (High Priority)
- **AI News** (High Priority)  
- **The Verge AI** (High Priority)
- **MIT Technology Review AI** (High Priority)
- **IEEE Spectrum AI** (Medium Priority)
- **VentureBeat AI** (Medium Priority)

### Scheduling

Default schedule: **8:00 AM UTC daily**

To change the schedule, edit `.github/workflows/daily-update.yml`:

```yaml
on:
  schedule:
    - cron: '0 8 * * *'  # Change this line
```

## 🧪 Testing

### Local Testing

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export ANTHROPIC_API_KEY="your_key_here"
   export NOTION_TOKEN="your_token_here"
   export NOTION_PAGE_ID="your_page_id_here"
   ```

3. **Run the agent**:
   ```bash
   python src/main.py
   ```

### Manual GitHub Actions

1. Go to **Actions** tab
2. Select "Daily AI News Update"
3. Click **Run workflow**
4. Monitor logs for any issues

## 💰 Cost Estimate

### Monthly Costs
- **GitHub Actions**: Free (for public repos)
- **Claude API**: ~$1-3/month for daily summaries
- **Notion API**: Free
- **Total**: ~$1-3/month

## 🔒 Security Best Practices

- ✅ Never commit API keys to repository
- ✅ Use GitHub Secrets for sensitive data
- ✅ Regularly rotate API keys
- ✅ Monitor API usage and costs

## 📄 License

This project is licensed under the MIT License.

---

**Made with ❤️ for the AI community**