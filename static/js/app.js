console.log("App JS loaded");

// ============================================================================
// Global App Object & Helpers
// ============================================================================
const App = {
    // Simple HTML escape function to prevent XSS
    escapeHTML(str) {
        if (typeof str !== 'string') return '';
        return str.replace(/[&<>"']/g, function (match) {
            return {
                '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
            }[match];
        });
    },

    /**
     * Formats text with WhatsApp-style markup into HTML.
     * Supports bold (*), italic (_), strikethrough (~), and monospace (```).
     * @param {string} text The raw text to format.
     * @returns {string} HTML-formatted string.
     */
    formatWhatsAppText(text) {
        let html = this.escapeHTML(text);

        // Note: Order matters for nested formatting.
        html = html
            .replace(/```([^`]+)```/g, '<code>$1</code>')         // Monospace
            .replace(/\*([^*]+)\*/g, '<strong>$1</strong>')       // Bold
            .replace(/_([^_]+)_/g, '<em>$1</em>')                 // Italic
            .replace(/~([^~]+)~/g, '<del>$1</del>');              // Strikethrough
        return html;
    }
};

// ============================================================================
// Dashboard Page Logic
// ============================================================================
App.Dashboard = {
    currentView: 'active', // 'active' or 'archived'
    allContacts: [],
    allQuickReplies: [],

    init() {
        const addContactForm = document.getElementById('addContactForm');
        if (addContactForm) {
            addContactForm.addEventListener('submit', this.handleAddContact);
        }

        const activeTab = document.getElementById('tab-active');
        const archivedTab = document.getElementById('tab-archived');
        if (activeTab && archivedTab) {
            activeTab.addEventListener('click', () => this.setView('active'));
            archivedTab.addEventListener('click', () => this.setView('archived'));
        }

        this.fetchData();
    },

    async fetchData() {
        const response = await fetch('/api/contacts');
        const data = await response.json();
        this.allContacts = data.contacts;
        this.allQuickReplies = data.quickreplies;
        this.renderContacts();
    },

    setView(view) {
        this.currentView = view;
        const activeTab = document.getElementById('tab-active');
        const archivedTab = document.getElementById('tab-archived');

        const activeClasses = ['border-indigo-500', 'text-indigo-600'];
        const inactiveClasses = ['border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300'];

        if (view === 'active') {
            activeTab.classList.add(...activeClasses);
            activeTab.classList.remove(...inactiveClasses);
            archivedTab.classList.add(...inactiveClasses);
            archivedTab.classList.remove(...activeClasses);
        } else {
            archivedTab.classList.add(...activeClasses);
            archivedTab.classList.remove(...inactiveClasses);
            activeTab.classList.add(...inactiveClasses);
            activeTab.classList.remove(...activeClasses);
        }

        this.renderContacts();
    },

    renderContacts() {
        const contactsList = document.getElementById('contacts-list');
        contactsList.innerHTML = '';

        const contactsToDisplay = this.allContacts.filter(contact => {
            const isSent = contact.status === 'Message Sent';
            return this.currentView === 'active' ? !isSent : isSent;
        });

        if (contactsToDisplay.length === 0) {
            const message = this.currentView === 'active' ? 'No active contacts. Add one above!' : 'No archived contacts yet.';
            contactsList.innerHTML = `<div class="bg-white shadow-md rounded-lg p-6 text-center text-gray-500"><p>${message}</p></div>`;
            return;
        }

        contactsToDisplay.forEach(contact => {
            let quickReplyButtons = `<p class="text-sm text-gray-500">No quick replies available. <a href="/quickreplies" class="text-indigo-600 hover:underline">Create one</a>.</p>`;
            if (this.allQuickReplies.length > 0) {
                quickReplyButtons = this.allQuickReplies.map(qr =>
                    `<button class="flex-grow px-3 py-2 border border-indigo-500 text-indigo-500 rounded-md hover:bg-indigo-500 hover:text-white text-sm" type="button" onclick="App.Dashboard.sendMessage(${contact.id}, ${qr.id})">${App.escapeHTML(qr.name)}</button>`
                ).join('');
            }

            // Only show send buttons for active contacts
            const actionArea = this.currentView === 'active' ? `
                <div class="border-t pt-3">
                    <div class="flex flex-wrap gap-2">${quickReplyButtons}</div>
                </div>` : '';

            const card = `
                <div class="bg-white shadow-md rounded-lg p-4">
                    <div class="flex justify-between items-center justify-between mb-3">
                        <div class="flex items-center font-semibold text-gray-900"> 
                            <div class="flex items-center space-x-2"> 
                                <a href="whatsapp://send/?phone=${App.escapeHTML(contact.number)}"><span class="material-symbols-outlined">chat</span></a> 
                                <div>${App.escapeHTML(contact.number)} </div>
                            </div>
                        </div>
                        <div class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${contact.status === 'Message Sent' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">${App.escapeHTML(contact.status)}</div>
                    </div>
                    ${actionArea}
                </div>`;
            contactsList.innerHTML += card;
        });
    },

    async handleAddContact(event) {
        event.preventDefault();
        const form = event.target;
        const textarea = form.querySelector('textarea[name="numbers"]');
        const formData = new FormData(form);
        const numbers = formData.get('numbers');

        const response = await fetch('/api/contacts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ numbers: numbers })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            textarea.value = ''; // Clear textarea
            App.Dashboard.fetchData(); // Refresh list
        } else {
            alert(`Error: ${result.error}`);
        }
    },

    sendMessage(contactId, templateId) {
        if (contactId && templateId) {
            // This still redirects, which is the desired behavior for sending a WhatsApp message.
            this.fetchData(); // Refresh list
            console.log(`Sending message to contact ID ${contactId} with template ID ${templateId}`);
            window.location.href = `/send/${contactId}/${templateId}`;
        }
    }
};

// ============================================================================
// Quick Replies Page Logic
// ============================================================================
App.QuickReplies = {
    API_URL: '/api/quickreplies',
    modal: null,

    init() {
        this.modal = document.getElementById('quickReplyModal');
        this.fetchQuickReplies();
    },

    async fetchQuickReplies() {
        const response = await fetch(this.API_URL);
        const quickReplies = await response.json();
        const list = document.getElementById('quickreplies-list');
        list.innerHTML = '';
        if (quickReplies.length === 0) {
            list.innerHTML = `<div class="bg-white shadow-md rounded-lg p-6 text-center text-gray-500"><p>No quick replies yet. Create one to get started!</p></div>`;
            return;
        }
        quickReplies.forEach(qr => {
            const card = `
                <div id="quickreply-card-${qr.id}" class="bg-white shadow-md rounded-lg p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="font-semibold text-gray-800">${App.escapeHTML(qr.name)}</p>
                            <p class="text-sm text-gray-600 mt-1 whitespace-pre-wrap">${App.formatWhatsAppText(qr.text)}</p>
                        </div>
                        <div class="flex-shrink-0 ml-4 space-x-2">
                            <button class="text-indigo-600 hover:text-indigo-900 text-sm font-medium" onclick='App.QuickReplies.prepareEditModal(${qr.id}, ${JSON.stringify(qr.name)}, ${JSON.stringify(qr.text)})'>Edit</button>
                            <button class="text-red-600 hover:text-red-900 text-sm font-medium" onclick="App.QuickReplies.deleteQuickReply(${qr.id})">Delete</button>
                        </div>
                    </div>
                </div>
            `;
            list.innerHTML += card;
        });
    },

    openModal() { this.modal.classList.remove('hidden'); },
    closeModal() { this.modal.classList.add('hidden'); },

    prepareCreateModal() {
        document.getElementById('quickReplyForm').reset();
        document.getElementById('quickReplyId').value = '';
        document.getElementById('quickReplyModalLabel').textContent = 'Create New Quick Reply';
        this.openModal();
    },

    prepareEditModal(id, name, text) {
        document.getElementById('quickReplyId').value = id;
        document.getElementById('quickReplyName').value = name;
        document.getElementById('quickReplyText').value = text;
        document.getElementById('quickReplyModalLabel').textContent = 'Edit Quick Reply';
        this.openModal();
    },

    async saveQuickReply() {
        const id = document.getElementById('quickReplyId').value;
        const name = document.getElementById('quickReplyName').value;
        const text = document.getElementById('quickReplyText').value;
        if (!name || !text) {
            alert('Name and Text are required.');
            return;
        }
        const isCreating = !id;

        const url = isCreating ? this.API_URL : `${this.API_URL}/${id}`;
        const method = isCreating ? 'POST' : 'PUT';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, text })
        });

        if (response.ok) {
            this.closeModal();
            this.fetchQuickReplies(); // Refresh the list
        } else {
            alert('Failed to save quick reply.');
        }
    },

    async deleteQuickReply(id) {
        if (confirm('Are you sure you want to delete this quick reply?')) {
            const response = await fetch(`${this.API_URL}/${id}`, { method: 'DELETE' });
            if (response.ok) {
                document.getElementById(`quickreply-card-${id}`).remove();
            } else {
                alert('Failed to delete quick reply.');
            }
        }
    }
};

// ============================================================================
// Page-specific Initializers
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.id;
    if (pageId === 'page-dashboard') {
        App.Dashboard.init();
    } else if (pageId === 'page-manage-quick-replies') {
        App.QuickReplies.init();
    }
});