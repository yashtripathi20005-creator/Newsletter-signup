import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for all routes

# Validate configuration on startup
try:
    Config.validate_config()
except ValueError as e:
    print(f"⚠️  Configuration Error: {e}")
    exit(1)


@app.route('/')
def index():
    """Render the signup form page."""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Newsletter API is running'
    }), 200


@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """
    Subscribe a user to the Mailchimp newsletter.
    
    Expects JSON payload:
    {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    try:
        # Get and validate request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Validate email
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            }), 400
        
        # Simple email validation
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Invalid email address format'
            }), 400
        
        # Prepare Mailchimp API request
        api_key = app.config['MAILCHIMP_API_KEY']
        audience_id = app.config['MAILCHIMP_AUDIENCE_ID']
        server_prefix = app.config['MAILCHIMP_SERVER_PREFIX']
        
        url = f'https://{server_prefix}.api.mailchimp.com/3.0/lists/{audience_id}/members'
        
        # Prepare subscriber data
        subscriber_data = {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': {}
        }
        
        # Add name fields if provided
        if first_name:
            subscriber_data['merge_fields']['FNAME'] = first_name
        if last_name:
            subscriber_data['merge_fields']['LNAME'] = last_name
        
        # Set status to 'pending' if double opt-in is enabled in Mailchimp
        # 'subscribed' adds directly, 'pending' sends confirmation email
        # We'll use 'subscribed' for immediate subscription
        # Change to 'pending' if you want double opt-in
        subscriber_data['status'] = 'subscribed'
        
        # Make API request
        headers = {
            'Authorization': f'apikey {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(subscriber_data),
            timeout=10
        )
        
        # Handle Mailchimp API response
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Successfully subscribed to the newsletter!'
            }), 200
        
        elif response.status_code == 400:
            error_data = response.json()
            error_detail = error_data.get('detail', '')
            
            # Check if user is already subscribed
            if 'already a list member' in error_detail:
                return jsonify({
                    'success': False,
                    'message': 'This email is already subscribed to our newsletter.'
                }), 409
            
            return jsonify({
                'success': False,
                'message': f'Subscription failed: {error_detail}'
            }), 400
        
        else:
            return jsonify({
                'success': False,
                'message': f'Server error: {response.status_code}'
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'Request timed out. Please try again.'
        }), 504
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'message': 'Connection error. Please check your internet connection.'
        }), 503
        
    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    """
    Unsubscribe a user from the newsletter.
    
    Expects JSON payload:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            }), 400
        
        # Prepare Mailchimp API request
        api_key = app.config['MAILCHIMP_API_KEY']
        audience_id = app.config['MAILCHIMP_AUDIENCE_ID']
        server_prefix = app.config['MAILCHIMP_SERVER_PREFIX']
        
        # Generate subscriber hash (MD5 of lowercase email)
        import hashlib
        subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
        
        url = f'https://{server_prefix}.api.mailchimp.com/3.0/lists/{audience_id}/members/{subscriber_hash}'
        
        headers = {
            'Authorization': f'apikey {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Update status to 'unsubscribed'
        response = requests.patch(
            url,
            headers=headers,
            data=json.dumps({'status': 'unsubscribed'}),
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Successfully unsubscribed from the newsletter.'
            }), 200
        elif response.status_code == 404:
            return jsonify({
                'success': False,
                'message': 'Email not found in our subscriber list.'
            }), 404
        else:
            return jsonify({
                'success': False,
                'message': f'Unsubscribe failed: {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        app.logger.error(f'Unsubscribe error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
