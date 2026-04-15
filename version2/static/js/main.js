// 更新购物车数量
function updateCartQuantity(productId, quantity) {
    fetch(`/cart/update/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    }).then(() => {
        location.reload();
    });
}

// 删除购物车商品
function removeCartItem(itemId) {
    if (confirm('确定要移除该商品吗？')) {
        window.location.href = `/cart/remove/${itemId}`;
    }
}

// 自动隐藏alert消息
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);
});

// 添加到购物车
function addToCart(productId) {
    const quantity = document.getElementById('quantity')?.value || 1;
    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    }).then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    });
}