"""
Notion Updater Module
Updates Notion page with the generated AI news summary
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionUpdater:
    def __init__(self):
        self.token = os.getenv('NOTION_TOKEN')
        self.page_id = os.getenv('NOTION_PAGE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"
        
        if not self.token:
            raise ValueError("NOTION_TOKEN environment variable is required")
        if not self.page_id:
            raise ValueError("NOTION_PAGE_ID environment variable is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Notion-Version': self.version
        }
    
    def convert_markdown_to_blocks(self, markdown_content: str) -> list:
        """Convert markdown content to Notion blocks"""
        blocks = []
        lines = markdown_content.split('\n')
        current_block = None
        
        for line in lines:
            line = line.strip()
            
            if not line:  # Empty line
                if current_block:
                    blocks.append(current_block)
                    current_block = None
                continue
            
            # Handle headings
            if line.startswith('## '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                }
            elif line.startswith('### '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                }
            # Handle bullet points
            elif line.startswith('- '):
                if current_block and current_block.get("type") != "bulleted_list_item":
                    blocks.append(current_block)
                    current_block = None
                
                content = line[2:]
                rich_text = self.parse_rich_text(content)
                
                block = {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": rich_text
                    }
                }
                blocks.append(block)
            # Handle regular paragraphs
            else:
                if current_block:
                    blocks.append(current_block)
                
                rich_text = self.parse_rich_text(line)
                current_block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": rich_text
                    }
                }
        
        # Add the last block
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def parse_rich_text(self, text: str) -> list:
        """Parse text with markdown formatting into Notion rich text format"""
        return [{"type": "text", "text": {"content": text}}]
    
    def clear_page_content(self) -> bool:
        """Clear existing content from the Notion page"""
        try:
            response = requests.get(
                f"{self.base_url}/blocks/{self.page_id}/children",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get page blocks: {response.text}")
                return False
            
            blocks = response.json().get('results', [])
            
            for block in blocks:
                delete_response = requests.delete(
                    f"{self.base_url}/blocks/{block['id']}",
                    headers=self.headers
                )
                if delete_response.status_code not in [200, 404]:
                    logger.warning(f"Failed to delete block {block['id']}")
            
            logger.info(f"Cleared {len(blocks)} blocks from page")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing page content: {e}")
            return False
    
    def update_page_content(self, markdown_content: str) -> bool:
        """Update the Notion page with new content"""
        try:
            if not self.clear_page_content():
                logger.warning("Failed to clear existing content, proceeding anyway")
            
            blocks = self.convert_markdown_to_blocks(markdown_content)
            
            chunk_size = 100
            for i in range(0, len(blocks), chunk_size):
                chunk = blocks[i:i + chunk_size]
                
                payload = {"children": chunk}
                
                response = requests.patch(
                    f"{self.base_url}/blocks/{self.page_id}/children",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to update page: {response.text}")
                    return False
            
            logger.info(f"Successfully updated Notion page with {len(blocks)} blocks")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Notion page: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Notion API"""
        try:
            response = requests.get(
                f"{self.base_url}/pages/{self.page_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("Successfully connected to Notion")
                return True
            else:
                logger.error(f"Failed to connect to Notion: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

if __name__ == "__main__":
    if os.getenv('NOTION_TOKEN') and os.getenv('NOTION_PAGE_ID'):
        updater = NotionUpdater()
        if updater.test_connection():
            print("✅ Notion connection successful")
        else:
            print("❌ Notion connection failed")
    else:
        print("Please set NOTION_TOKEN and NOTION_PAGE_ID environment variables")