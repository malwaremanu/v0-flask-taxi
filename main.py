from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import urllib.parse

# Create an instance of the Flask class
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# In-memory storage instead of a database
contacts = []  # List of dicts: [{'id': 1, 'number': '1234567890', 'status': 'New'}]
quickreplies = [] # List of dicts: [{'id': 1, 'name': 'Greeting', 'text': 'Hello!'}]
next_contact_id = 1
next_quickreply_id = 1

d = """
🚖 Hello!
Now book your rides quickly and affordably with our new [App Name] Taxi App 🚕✨
✅ Fast & reliable pickups
✅ Affordable fares
✅ 24/7 service
✅ Track your driver live on map
Download now and enjoy your first ride at a special discount! 🎉
👉 [Download Link]
Need a ride? We’re just one tap away!
"""
# Add some sample data for demonstration
if not quickreplies: # To prevent duplication on reload
    quickreplies.append({'id': 1, 'name': 'Welcome', 'text': 'Hello!\nWelcome to our service.'})
    quickreplies.append({'id': 2, 'name': 'Offer', 'text': d})
    next_quickreply_id = 3
    contacts.append({'id': 1, 'number': '9024343890', 'status': 'New'})
    next_contact_id = 2

@app.route('/')
def dashboard():
    """Renders the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/contacts', methods=['GET', 'POST'])
def handle_contacts():
    """API endpoint for fetching and adding contacts."""
    global next_contact_id
    if request.method == 'POST':
        data = request.get_json()
        numbers_str = data.get('numbers')
        if numbers_str:
            numbers = [num.strip() for num in numbers_str.split(',') if num.strip().isdigit()]
            added_count = 0
            for number in numbers:

                if len(number) != 10:
                    continue  # Skip invalid numbers                    
                # Avoid adding duplicate numbers
                if not any(c['number'] == number for c in contacts):
                    contacts.append({'id': next_contact_id, 'number': number, 'status': 'New'})
                    next_contact_id += 1
                    added_count += 1
            return jsonify({'message': f'Added {added_count} new contact(s).'}), 200
        return jsonify({'error': 'No numbers provided'}), 400
    
    # GET request
    return jsonify({'contacts': contacts, 'quickreplies': quickreplies})

@app.route('/send/<int:contact_id>/<int:quickreply_id>')
def send_message(contact_id, quickreply_id):
    """
    Updates contact status and redirects to WhatsApp.
    """
    contact = next((c for c in contacts if c['id'] == contact_id), None)
    quickreply = next((q for q in quickreplies if q['id'] == quickreply_id), None)

    if not contact or not quickreply:
        # This redirect will show the dashboard, but we can't easily show an alert.
        # The best we can do without a more complex state management is to flash here.
        flash('Contact or Quick Reply not found!', 'danger') # Kept for this edge case
        return redirect(url_for('dashboard')) 

    # Update status
    contact['status'] = 'Message Sent'

    # Create wa.me link
    phone_number = f"91{contact['number']}"
    message_text = urllib.parse.quote(quickreply['text'], encoding='utf-8')
    # Using https://wa.me/ is more robust across desktop and mobile devices
    #whatsapp_url = f"https://wa.me/{phone_number}?text={message_text}"
    whatsapp_url = f"whatsapp://send/?phone={phone_number}&text={message_text}"
    return redirect(whatsapp_url)


# --- Quick Replies Page ---
@app.route('/quickreplies')
def quickreplies_page():
    """Renders the single-page quick reply management UI."""
    return render_template('quickreplies.html', title="Manage Quick Replies")

# --- Quick Reply API Endpoints (Consolidated) ---
@app.route('/api/quickreplies', methods=['GET', 'POST'])
def handle_quickreplies():
    """API endpoint to get all quick replies or create a new one."""
    global next_quickreply_id
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('name') or not data.get('text'):
            return jsonify({'error': 'Missing data'}), 400
        
        new_quickreply = {'id': next_quickreply_id, 'name': data['name'], 'text': data['text']}
        quickreplies.append(new_quickreply)
        next_quickreply_id += 1
        return jsonify(new_quickreply), 200
    else: # GET request
        return jsonify(quickreplies)

@app.route('/api/quickreplies/<int:quickreply_id>', methods=['PUT', 'DELETE'])
def handle_quickreply_by_id(quickreply_id):
    """API endpoint to edit or delete a specific quick reply."""
    global quickreplies
    quickreply = next((q for q in quickreplies if q['id'] == quickreply_id), None)
    if not quickreply:
        return jsonify({'error': 'Quick Reply not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing data'}), 400
        quickreply['name'] = data.get('name', quickreply['name'])
        quickreply['text'] = data.get('text', quickreply['text'])
        return jsonify(quickreply)
    
    if request.method == 'DELETE':
        quickreplies = [q for q in quickreplies if q['id'] != quickreply_id]
        return jsonify({'success': True})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80, debug=True)
import os     
def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()