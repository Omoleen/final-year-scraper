console.log('Hello')

var updatebtns = document.getElementsByClassName('saved-items')
console.log(updatebtns)

for (var i = 0; i < updatebtns.length; i++){
    updatebtns[i].addEventListener('click', function(){
        var productID = this.dataset.product
        var action = this.dataset.action
        var name = this.dataset.name
        var store = this.dataset.store
        var link = this.dataset.link
        var price = this.dataset.price
        var image = this.dataset.image
        console.log('productID:', productID, 'Action:', action,'name:', name, 'store:', store,'link:', link, 'price:', price,'image:', image)

        console.log('USER:', user)
        if(user == 'AnonymousUser'){
            console.log('User is not authenticated')
        }else{
            updateUserOrder(productID, action, name, store, link, price, image)
        }
    })
}


function updateUserOrder(productId, action, name, store, link, price, image){
    console.log('User authent')

    var url = '/update_item/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'action':action,'name':name, 'store':store,'link':link, 'price':price, 'image':image})
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('data', data)
            // location.reload()
        });
}