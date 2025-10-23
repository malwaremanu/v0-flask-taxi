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

aa = """
NAVEEN TAXI SERVICE – JAIPUR
आपकी हर संभव सहायता के लिए सदैव तत्पर है।

🚘 सेवाएँ:
* जयपुर से हरिद्वार, दिल्ली, आगरा, अजमेर, कोटा, उदयपुर आदि के लिए One Way / Round Trip टैक्सी सेवा
* साफ़-सुथरी गाड़ियाँ व अनुभवी ड्राइवर्स
* 📦 पार्सल सेवा (24×7) – मिठाई, कपड़े, दस्तावेज़ आदि
* 👨‍✈️ यदि आपकी स्वयं की गाड़ी है, तो हम डेली वेज बेसिस पर अस्थायी ड्राइवर (Temporary Driver) भी उपलब्ध कराते हैं

📞 9460145006 | 9521890614

🙏 हम आपकी यात्रा को सुरक्षित, सहज और समय पर पूरा कराने का वचन देते हैं।
ईश्वर आपके परिवार को शक्ति और शांति प्रदान करें।
"""

a = """
🙏 शोक संवेदना सहित 🙏
आपके परिवार में हुए दुखद निधन की ख़बर सुनकर हमें गहरा दुःख हुआ।
ईश्वर दिवंगत आत्मा को शांति दे और आपको इस कठिन समय में धैर्य एवं शक्ति प्रदान करे।

यदि आप हरिद्वार या किसी अन्य स्थान पर अंतिम संस्कार हेतु यात्रा पर जा रहे हैं, तो
NAVEEN TAXI SERVICE – JAIPUR
आपकी हर संभव सहायता के लिए सदैव तत्पर है।

🚘 सेवाएँ:
* जयपुर से हरिद्वार, दिल्ली, आगरा, अजमेर, कोटा, उदयपुर आदि के लिए One Way / Round Trip टैक्सी सेवा
* साफ़-सुथरी गाड़ियाँ व अनुभवी ड्राइवर्स
* 📦 पार्सल सेवा (24×7) – मिठाई, कपड़े, दस्तावेज़ आदि
* 👨‍✈️ यदि आपकी स्वयं की गाड़ी है, तो हम डेली वेज बेसिस पर अस्थायी ड्राइवर (Temporary Driver) भी उपलब्ध कराते हैं

📞 9460145006 | 9521890614

🙏 हम आपकी यात्रा को सुरक्षित, सहज और समय पर पूरा कराने का वचन देते हैं।
ईश्वर आपके परिवार को शक्ति और शांति प्रदान करें।
"""

b = """
🙏 गहरी संवेदना सहित 🙏  
आपके परिवार में हुए दुःखद निधन की खबर से मन व्यथित हुआ।  
ईश्वर आत्मा को मोक्ष और परिवार को धैर्य प्रदान करें।

हरिद्वार या अन्य स्थान पर अंतिम संस्कार हेतु यात्रा के लिए  
यदि वाहन की आवश्यकता हो, तो NAVEEN TAXI SERVICE – JAIPUR आपकी सहायता कर सकता है।

🚘 हमारी सेवाएँ:
• One Way / Round Trip टैक्सी सेवा (जयपुर से विभिन्न शहरों तक)  
• प्रशिक्षित ड्राइवर एवं स्वच्छ वाहन  
• 📦 24×7 पार्सल डिलीवरी – कपड़े, दस्तावेज़, मिठाई आदि  
• 👨‍✈️ अस्थायी ड्राइवर सुविधा भी उपलब्ध

📞 9460145006 | 9521890614

हम आपके दुःख में सहभागी हैं और हर संभव मदद के लिए उपलब्ध हैं।
"""

c = """
🙏 हमारी शोक संवेदनाएँ 🙏  
आपके परिवार के किसी प्रिय सदस्य के निधन का समाचार सुनकर गहरा दुःख हुआ।  
ईश्वर आत्मा को शांति दे और आपको यह कठिन समय सहने की शक्ति दे।

यदि आप हरिद्वार या किसी अन्य स्थान पर यात्रा पर जा रहे हैं,  
तो NAVEEN TAXI SERVICE – JAIPUR आपकी सुविधा के लिए तैयार है।

🚘 सुविधाएँ:
• जयपुर से हरिद्वार, दिल्ली, आगरा, कोटा, अजमेर, उदयपुर आदि मार्गों पर टैक्सी सेवा  
• स्वच्छ कारें, अनुभवी ड्राइवर  
• 📦 24×7 पार्सल डिलीवरी सेवा  
• 👨‍✈️ Temporary Driver सुविधा भी उपलब्ध

📞 9460145006 | 9521890614

हम आपके परिवार की शांति व सुरक्षा की कामना करते हैं।
"""

d = """
🙏 शोक संदेश 🙏  
आपके परिवार में हुए निधन से हमें गहरा दुःख पहुँचा है।  
ईश्वर दिवंगत आत्मा को शांति और आपको धैर्य प्रदान करे।

यदि आप हरिद्वार या अन्य शहर यात्रा हेतु जा रहे हैं,  
तो NAVEEN TAXI SERVICE – JAIPUR हर प्रकार की सहायता प्रदान करने को तत्पर है।

🚘 सेवाएँ:
• One Way / Round Trip टैक्सी – जयपुर से हरिद्वार, दिल्ली, आगरा, कोटा, अजमेर आदि  
• साफ-सुथरी गाड़ियाँ और विनम्र ड्राइवर्स  
• 📦 24 घंटे पार्सल सेवा – दस्तावेज़, कपड़े, मिठाई आदि  
• 👨‍✈️ अस्थायी ड्राइवर सेवा (Daily Basis)

📞 9460145006 | 9521890614

🙏 ईश्वर आपके परिवार को शक्ति और दिवंगत आत्मा को शांति दें।
"""

# Add some sample data for demonstration
if not quickreplies: # To prevent duplication on reload
    quickreplies.append({'id': 1, 'name': 'Hello', 'text': aa})
    quickreplies.append({'id': 2, 'name': 'd1', 'text': a})
    quickreplies.append({'id': 3, 'name': 'd2', 'text': b})
    quickreplies.append({'id': 4, 'name': 'd3', 'text': c})
    quickreplies.append({'id': 5, 'name': 'd4', 'text': d})

    next_quickreply_id = 5
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
            # print(numbers_str.split('\n'))
            if "," in numbers_str:
                numbers = [num.strip() for num in numbers_str.split(',') if num.strip().isdigit()] 

            elif "\n" in numbers_str:
                numbers = [num.strip() for num in numbers_str.split('\n') if num.strip().isdigit()] 
            
            else:
                numbers = []

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
        return jsonify({'error': 'No numbers provided, please use proper format.'}), 400
    
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
    whatsapp_url = f"whatsapp://send/?phone={phone_number}&text=🙏 {phone_number}, {message_text}"
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
    app.run(port=int(os.environ.get('PORT', 50001)))

if __name__ == "__main__":
    main()