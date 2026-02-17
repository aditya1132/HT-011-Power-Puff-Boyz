# OpenAI Integration Setup

## Environment Configuration

To enable OpenAI integration in your AI Mental Health Companion, you need to add the OpenAI API key to your environment configuration.

### Required Environment Variable

Add the following to your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
```

### How to Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### Important Security Notes

- **NEVER** commit your API key to version control
- Keep your `.env` file in `.gitignore`
- Use different API keys for development and production
- Monitor your API usage and set billing limits

### Fallback Behavior

If no OpenAI API key is provided:
- The system will automatically fall back to template-based responses
- All existing functionality will continue to work
- You'll see a log message: "No OpenAI API key found. Using template-based responses."

### API Usage and Costs

- The integration uses the `gpt-4o-mini` model for cost efficiency
- Response length is limited to ~200 words to control costs
- Requests have a 10-second timeout for reliability
- Monitor your usage on the OpenAI dashboard

### Testing the Integration

1. Add your API key to `.env`
2. Restart your FastAPI server
3. Look for the log message: "OpenAI client initialized successfully"
4. Send a test message and check the response type in the API response

The `response_type` field will show:
- `"ai_supportive"` - OpenAI-generated response
- `"template_supportive"` - Template-based fallback
- `"crisis_intervention"` - Crisis response (always uses templates)

### Error Handling

If OpenAI API calls fail:
- The system automatically falls back to template responses
- Errors are logged for debugging
- Users receive a seamless experience without interruption