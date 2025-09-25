# 🤖 SMIED AI Teaching Assistant

## Overview

SMIED is an intelligent AI teaching assistant integrated into the School Management System that helps teachers with lesson planning, educational strategies, and classroom management. Powered by ChatGPT 4.0 via RapidAPI, it provides real-time assistance during lesson creation and planning.

## ✨ Features

### 🎯 Core Capabilities
- **Lesson Planning Assistance**: Help with structuring lessons, creating objectives, and organizing content
- **Teaching Strategies**: Suggest engagement techniques, differentiation methods, and assessment approaches
- **Curriculum Support**: Understands Nigerian education standards and curriculum requirements
- **Real-time Context**: Analyzes current lesson form data to provide relevant suggestions
- **Interactive Interface**: Modern, responsive chat interface with typing indicators and quick suggestions

### 🎨 User Interface
- **Floating Chat Widget**: Non-intrusive floating button that expands into a full chat interface
- **Modern Design**: Clean, professional design with gradient colors and smooth animations
- **Quick Suggestions**: Pre-defined question chips for common teaching scenarios
- **Typing Indicators**: Visual feedback when AI is processing requests
- **Message History**: Maintains conversation context throughout the session

## 🚀 How to Use

### For Teachers

1. **Access the Chatbot**:
   - Navigate to the "Create Lesson" page
   - Click the floating robot icon (🤖) in the bottom-right corner
   - Or click the "AI Assistant" button on the teacher dashboard

2. **Ask Questions**:
   - Type your question in the input field
   - Click the send button or press Enter
   - Use the quick suggestion chips for common questions

3. **Get Contextual Help**:
   - The AI automatically analyzes your current lesson form
   - Provides suggestions based on your subject, grade level, and objectives
   - Offers specific advice for your teaching context

### Example Questions

- "How can I make my mathematics lesson more engaging?"
- "Help me write learning objectives for this lesson"
- "What assessment methods should I use?"
- "How can I differentiate this lesson for different learning levels?"
- "Suggest activities for teaching fractions to Basic 5 students"

## 🔧 Technical Implementation

### Backend API
- **Endpoint**: `/api/teacher/ai-chatbot`
- **Method**: POST
- **Authentication**: Required (Teacher role only)
- **Integration**: ChatGPT 4.0 via RapidAPI

### Frontend Components
- **Location**: `templates/teacher/create_lesson.html`
- **Styling**: Custom CSS with modern design
- **JavaScript**: Vanilla JS for chat functionality
- **Responsive**: Works on desktop and mobile devices

### API Integration
```python
# Example API call
POST /api/teacher/ai-chatbot
{
    "message": "How can I make my lesson more engaging?",
    "context": "Current lesson: Mathematics, Basic 5, Fractions"
}
```

## 🛠️ Setup and Configuration

### Prerequisites
- Flask application running
- Teacher account with proper authentication
- Internet connection for API calls
- RapidAPI ChatGPT subscription

### API Configuration
The chatbot uses the following RapidAPI configuration:
- **Host**: `chatgpt-42.p.rapidapi.com`
- **Endpoint**: `/aitohuman`
- **API Key**: Configured in the code (should be moved to environment variables for production)

### Environment Variables (Recommended)
```bash
RAPIDAPI_KEY=your_rapidapi_key_here
CHATGPT_API_HOST=chatgpt-42.p.rapidapi.com
```

## 📱 User Interface Details

### Chat Widget Design
- **Position**: Fixed bottom-right corner
- **Size**: 350px wide × 500px tall
- **Colors**: Purple gradient theme (#667eea to #764ba2)
- **Animation**: Smooth slide-in/out transitions

### Message Types
- **User Messages**: Right-aligned with blue background
- **AI Messages**: Left-aligned with white background
- **System Messages**: Welcome message and error notifications

### Quick Suggestions
Pre-defined question chips for common scenarios:
- Engagement strategies
- Learning objectives
- Assessment ideas
- Differentiation techniques

## 🔒 Security and Privacy

### Authentication
- Only authenticated teachers can access the chatbot
- API calls are validated on the server side
- No sensitive data is stored in chat history

### Data Handling
- Chat messages are not permanently stored
- Form context is only sent during active sessions
- API responses are processed server-side

## 🧪 Testing

### Manual Testing
1. Start the Flask application
2. Login as a teacher
3. Navigate to Create Lesson page
4. Click the AI Assistant button
5. Test various questions and scenarios

### Automated Testing
Run the test script:
```bash
python test_ai_chatbot.py
```

### Test Scenarios
- Basic functionality test
- API connection test
- Error handling test
- Context analysis test

## 🚨 Troubleshooting

### Common Issues

1. **Chatbot not appearing**:
   - Check if you're logged in as a teacher
   - Verify JavaScript is enabled
   - Check browser console for errors

2. **API errors**:
   - Verify internet connection
   - Check RapidAPI key validity
   - Review server logs for detailed errors

3. **Slow responses**:
   - Check network connection
   - Verify API service status
   - Consider implementing response caching

### Error Messages
- "AI service temporarily unavailable" - API connection issue
- "Access denied" - Authentication problem
- "Failed to process request" - Server-side error

## 🔮 Future Enhancements

### Planned Features
- **Voice Input**: Speech-to-text for hands-free interaction
- **File Upload**: Analyze uploaded lesson materials
- **Multi-language Support**: Support for different languages
- **Advanced Context**: Integration with student performance data
- **Lesson Templates**: AI-generated lesson plan templates

### Potential Integrations
- **Curriculum Database**: Direct integration with curriculum standards
- **Resource Library**: Access to educational resources
- **Collaboration**: Share AI suggestions with other teachers
- **Analytics**: Track AI usage and effectiveness

## 📊 Performance Considerations

### Optimization
- **Caching**: Implement response caching for common questions
- **Rate Limiting**: Prevent API abuse
- **Async Processing**: Handle multiple requests efficiently
- **Error Recovery**: Graceful handling of API failures

### Monitoring
- Track API usage and costs
- Monitor response times
- Log error rates and types
- User engagement metrics

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies
3. Configure API keys
4. Run the application
5. Test chatbot functionality

### Code Structure
- **Backend**: `app.py` (API endpoint)
- **Frontend**: `templates/teacher/create_lesson.html`
- **Styling**: Embedded CSS in template
- **JavaScript**: Embedded in template

### Adding Features
1. Modify the API endpoint for new functionality
2. Update the frontend interface
3. Add appropriate error handling
4. Test thoroughly
5. Update documentation

## 📞 Support

For issues or questions about the AI Chatbot feature:
1. Check the troubleshooting section
2. Review server logs
3. Test with the provided test script
4. Contact the development team

---

**Note**: This feature requires an active RapidAPI subscription and internet connection. The AI responses are generated by ChatGPT and should be reviewed for accuracy and appropriateness before use in educational settings.
