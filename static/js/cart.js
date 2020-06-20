const updateButtons = document.querySelectorAll('.update-cart');

updateButtons.forEach(button => {
    button.addEventListener('click', function (event) {
        const productId = this.dataset.product;
        const action = this.dataset.action;

        if (user === 'AnonymousUser') {
            addCookieItem(productId, action)
        } else {
            updateUserOrder(productId, action);
        }
    })
});

const addCookieItem = (productId, action) => {
    if (action === 'add') {
        if (cart[productId] === undefined) {
            cart[productId] = { quantity: 1 };
        } else {
            cart[productId].quantity += 1
        }
    } else if (action === 'remove') {
        cart[productId].quantity -= 1
        if (cart[productId].quantity <= 0) {
            delete cart[productId];
        }
    }
    document.cookie = `cart=${JSON.stringify(cart)};domain=;path=/`;
    location.reload();
}

const updateUserOrder = (productId, action) => {
    const url = '/update_item/';

    const body = {
        'productId': productId,
        'action': action
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(body)
    }).then(response => {
        return response.json();
    }).then(data => {
        location.reload();
    })
}