
// Basic Project Configuration
// see  the docs for more info: https://docs.basic.tech

// Project: braas
// Link: https://app.basic.tech/project/a9cf1e85-1cb1-461e-9c04-fcb5e0908369


export const schema = {
  "project_id": "a9cf1e85-1cb1-461e-9c04-fcb5e0908369",
  "tables": {
    "video": {
      "type": "collection",
      "fields": {
        "prompt": {
          "type": "string",
          "indexed": true
        },
        "description": {
          "type": "string",
          "indexed": true
        },
        "content": {
          "type": "string",
          "indexed": true
        },
        "metadata": {
          "type": "json",
          "indexed": true
        }
      }
    },
    "prompts": {
      "type": "collection",
      "fields": {
        "topic": {
          "type": "string",
          "indexed": true
        },
        "output": {
          "type": "string",
          "indexed": true
        }
      }
    }
  },
  "version": 1
}