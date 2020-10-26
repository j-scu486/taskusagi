const messagesContainer = document.querySelector('.messages');
    const booking_id = {{ booking_id }}
    const receiverId = {{ receiver_id }}
    let messagesId;
    

    // RECEIVE messages

    fetch(`messages/json/${booking_id}`)
        .then(response => response.json())
        .then(data => {
            let messages = [...data]
            // Set up initial messages
            messages.forEach(message => {
                messagesContainer.innerHTML += `
                    <div>${message.sent}</div>
                    <div>${message.message}</div>
                `
            })
            // Messages ID that will be used to filter new messages
            messagesId = messages.map(message => {
                return message.id
            })
        }
        )

    // Ajax call every 3 seconds to check for new messages and update template
    setInterval(function() {
    fetch(`messages/json/${booking_id}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(new_message => {
                if(messagesId.indexOf(new_message.id) == -1) {
                    // New message
                    messagesId.push(new_message.id)
                    messagesContainer.innerHTML += `
                    <div>${new_message.sent}</div>
                    <div>${new_message.message}</div>
                `
                }
            })
        }
        )
    }, 3000) 

    // SEND new message
    const submitMessage = document.querySelector('#send-message');
    
    submitMessage.addEventListener('submit', function(e) {
        const message = document.querySelector('#id_message').value;
        data = {
            'message': message,
            'receiver_id': receiverId,
        }

        e.preventDefault()
        fetch(`messages/json/send_message/${booking_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },

            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => console.log(data))
    })