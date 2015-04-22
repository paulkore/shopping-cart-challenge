var appModule = angular.module("ShoppingCartChallenge", ['ngCookies']);

appModule.run( function run( $http, $cookies ){

    // For CSRF token compatibility with Django
    $http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
});

appModule.controller("OrderController", function($scope, $location, $http) {

        $scope.orderId = null;
        $scope.orderStatus = 'EDIT';
        $scope.orderTotal = null;
        $scope.orderProducts = null;
        $scope.catalogueProducts = null;
        $scope.formProducts = null;
        $scope.ajaxError = null;


        // Decide whether it's a new or an existing order based on the URL; This is bad, but it'll do for now.
        // TODO: Look into Angular routing to implement properly.
        var url = $location.absUrl();
        if (!url.contains('orders/new')) {
            // This ID extraction code grabs the right-most numeric value
            // TODO: improve, because this is unreliable (the next numeric value is the port number)
            var numericValues = url.match( /\d+/g);
            $scope.orderId = Number(numericValues.last());
        }



        // expose function for click handlers
        $scope.onClickPrepareForm = prepareForm;
        $scope.onClickReviewOrder = reviewOrder;
        $scope.onClickModifyOrder = modifyOrder;
        $scope.onClickConfirmOrder = confirmOrder;




        // decider function: to display order total or not
        $scope.displayTotal = function() {
            return $scope.orderStatus == 'REVIEW' || $scope.orderStatus == 'CONFIRMED';
        };


        // Toggle dev controls
        $scope.showDevControls = false;

        // Issue the AJAX data load automatically (can be switched on/off)
        var autoLoad = true;
        if (autoLoad) {
            console.log('auto load (AJAX)');
            prepareForm();
        }



        function prepareForm() {
            if ($scope.orderId) {
                prepareExistingOrderForm();
            }
            else {
                prepareNewOrderForm();
            }
        }

        function prepareNewOrderForm() {
            console.log('preparing form for new order');

            loadCatalogueProducts().then(function() {
                $scope.formProducts = [];

                for (var i=0; i<$scope.catalogueProducts.length; i++) {
                    var formProduct = {};
                    formProduct.product = $scope.catalogueProducts[i];
                    formProduct.check = false;
                    formProduct.quantity = null;
                    $scope.formProducts.push(formProduct);
                }
            });
        }

        function prepareExistingOrderForm() {
            console.log('preparing form for existing order');

            loadExistingOrder().then(function(){
                $scope.formProducts = [];

                if ($scope.orderStatus == 'CONFIRMED' || $scope.orderStatus == 'REVIEW') {
                    console.log('preparing form for order in review, or confirmed order');

                    for (var i=0; i<$scope.orderProducts.length; i++) {
                        var orderProduct = $scope.orderProducts[i];

                        var formProduct = {};
                        formProduct.product = orderProduct.product;
                        formProduct.check = true;
                        formProduct.quantity = orderProduct.quantity;
                        $scope.formProducts.push(formProduct);
                    }
                }
                else if ($scope.orderStatus == 'EDIT') {
                    console.log('preparing form for order being edited - need to load the catalogue');

                    loadCatalogueProducts().then(function() {
                        console.log('applying existing order data to blank order from');

                        // 'new order' form used as a base for 'edit order' form
                        for (var i=0; i < $scope.catalogueProducts.length; i++) {
                            var formProduct = {};
                            formProduct.product = $scope.catalogueProducts[i];
                            formProduct.check = false;
                            formProduct.quantity = null;
                            $scope.formProducts.push(formProduct);
                        }

                        // populate the blank form with data from the existing order
                        for (var j=0; j<$scope.orderProducts.length; j++) {
                            var orderProduct = $scope.orderProducts[j];
                            var formProd = findFormProduct(orderProduct.product.id);

                            formProd.check = true;
                            formProd.quantity = orderProduct.quantity;
                        }
                    });
                }
                else {
                    console.error('Unhandled order status: ' + $scope.orderStatus)
                }

            });

        }

        function loadCatalogueProducts() {
            console.log('loading list of all products');

            $scope.catalogueProducts = null;
            $scope.ajaxError = null;

            var promise = $http.get("/api/products");
            promise.success(function(data) {
                $scope.catalogueProducts = [];
                for (var i=0; i<data.length; i++) {
                    var product_data = data[i];
                    var product = {};
                    product.id = product_data['id'];
                    product.name = product_data['name'];
                    product.price = product_data['price'];
                    $scope.catalogueProducts.push(product)
                }
            });
            promise.error(function(data) {
                $scope.ajaxError = 'Could not load data (AJAX call failed)';
            });

            return promise;
        }

        function loadExistingOrder() {
            console.log('loading data for existing order: ' + $scope.orderId);

            $scope.orderProducts = null;
            $scope.orderTotal = null;
            $scope.ajaxError = null;

            var promise = $http.get("/api/orders/" + $scope.orderId);
            promise.success(function(data) {
                $scope.orderStatus = data['order_status'];
                $scope.orderTotal = data['order_total'];
                $scope.orderProducts = data['products'];
            });
            promise.error(function(data) {
                $scope.ajaxError = 'Could not load data (AJAX call failed)';
            });

            return promise;
        }

        function findFormProduct(productId) {
            // TODO: sequential search... not ideal, but it will do for now.
            for (var i=0; i<$scope.formProducts.length; i++) {
                var formProduct = $scope.formProducts[i];
                if (formProduct.product.id == productId) {
                    return formProduct;
                }
            }

            console.error('form product not found for id: ' + productId);
            return null;
        }

        function modifyOrder() {
            console.log('submitting order: modify');

            var postData = {};
            postData.order_status = 'EDIT';
            postData.product_quantities = [];

            submitOrderData(getPOSTUrl(), postData);
        }

        function reviewOrder() {
            console.log('submitting order: review');

            var postData = {};
            postData.order_status = 'REVIEW';
            postData.product_quantities = [];
            for (var i=0; i<$scope.formProducts.length; i++) {
                var formProduct = $scope.formProducts[i];
                if (formProduct.check && formProduct.quantity && formProduct.quantity > 0) {
                    var pq_item = {
                        quantity: formProduct.quantity,
                        product_id: formProduct.product.id
                    };
                    postData.product_quantities.push(pq_item);
                }
            }

            submitOrderData(getPOSTUrl(), postData);
        }

        function confirmOrder() {
            console.log('submitting order: confirm');

            var postData = {};
            postData.order_status = 'CONFIRMED';
            postData.product_quantities = [];

            submitOrderData(getPOSTUrl(), postData);
        }

        function getPOSTUrl() {
            if ($scope.orderId) {
                return '/api/orders/' + $scope.orderId
            }
            else {
                return '/api/orders';
            }
        }

        function submitOrderData(postUrl, postData) {
            console.log('Submitting form (POST request via AJAX)');

            $scope.ajaxError = null;

            var promise = $http.post(postUrl, postData);
            promise.success(function(data, status, headers, config) {
                console.log('POST request returned successfully');
                if (data['order_id']) {
                    $scope.orderId = data['order_id'];
                    prepareForm();
                }
                else {
                    $scope.ajaxError = 'Unexpected data returned from (AJAX call failed)';
                }
            });
            promise.error(function(data, status, headers, config) {
                $scope.ajaxError = 'Could not load data (AJAX call failed)';
            });
        }



    });
