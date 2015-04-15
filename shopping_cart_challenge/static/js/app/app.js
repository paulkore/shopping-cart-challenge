appModule = angular.module("ShoppingCartChallenge", []);

appModule.controller("OrderController", function($scope, $location, $http) {

        $scope.formTitle = 'New order';
        $scope.orderId = null;
        $scope.orderStatus = 'EDIT';
        $scope.orderTotal = null;
        $scope.orderProducts = null;
        $scope.catalogueProducts = null;
        $scope.formProducts = null;
        $scope.ajaxError = null;

        // decide whether it's a new or an existing order based on the URL
        // (this feels wrong, but it'll do for now)
        $scope.url = $location.absUrl();
        console.log('url = ' + $scope.url);
        if (!$scope.url.contains('orders/new')) {
            $scope.formTitle = 'Existing order'

            // TODO: improve this ID extraction code, as it is unreliable (it grabs the right-most numeric value)
            var numericValues = $scope.url.match( /\d+/g);
            $scope.orderId = Number(numericValues.last());
        }


        $scope.loadCatalogueProducts = function() {
            console.log('loading list of all products');

            $scope.catalogueProducts = null;
            $scope.ajaxError = null;

            var promise = $http.get("/api/products");
            promise.success(function(data) {
                $scope.catalogueProducts = [];
                for (var i=0; i<data.length; i++) {
                    var product_data = data[i];
                    var product = {};
                    product.id = product_data.id;
                    product.name = product_data.name;
                    product.price = product_data.price;
                    $scope.catalogueProducts.push(product)
                }
            });
            promise.error(function(data) {
                $scope.ajaxError = 'Could not load data (AJAX call failed)';
            });

            return promise;
        };

        $scope.loadExistingOrder = function() {
            console.log('loading data for existing order: ' + $scope.orderId);

            $scope.orderProducts = null;
            $scope.orderTotal = null;
            $scope.ajaxError = null;

            var promise = $http.get("/api/orders/" + $scope.orderId);
            promise.success(function(data) {
                $scope.orderStatus = data.order_status;
                $scope.orderTotal = data.order_total;
                $scope.orderProducts = data.products;
            });
            promise.error(function(data) {
                $scope.ajaxError = 'Could not load data (AJAX call failed)';
            });

            return promise;
        };


        $scope.prepareNewOrderForm = function() {
            console.log('preparing form for new order');

            $scope.loadCatalogueProducts().then(function() {
                $scope.formProducts = [];

                for (var i=0; i<$scope.catalogueProducts.length; i++) {
                    var formProduct = {};
                    formProduct.product = $scope.catalogueProducts[i];
                    formProduct.check = false;
                    formProduct.quantity = null;
                    $scope.formProducts.push(formProduct);
                }
            });
        };

        $scope.prepareExistingOrderForm = function() {
            console.log('preparing form for existing order');

            $scope.loadExistingOrder().then(function(){
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

                    $scope.loadCatalogueProducts().then(function() {

                        // 'new order' form used as a base for 'edit order' form
                        for (var i=0; i<$scope.catalogueProducts.length; i++) {
                            var formProduct = {};
                            formProduct.product = $scope.catalogueProducts[i];
                            formProduct.check = false;
                            formProduct.quantity = null;
                            $scope.formProducts.push(formProduct);
                        }

                        // populate the blank form with data from the existing order
                        for (var j=0; j<$scope.orderProducts.length; j++) {
                            var orderProduct = $scope.orderProducts[j];
                            var formProd = $scope.findFormProduct(orderProduct.product.id);

                            formProd.check = true;
                            formProd.quantity = orderProduct.quantity;
                        }
                    });
                }
                else {
                    console.error('Unhandled order status: ' + $scope.orderStatus)
                }

            });

        };

        $scope.findFormProduct = function(productId) {
            // TODO: sequential search... not ideal, but it will do for now.
            for (var i=0; i<$scope.formProducts.length; i++) {
                var formProduct = $scope.formProducts[i];
                if (formProduct.id === productId) {
                    return formProduct;
                }
            }

            console.error('form product not found for id: ' + productId);
            return null;
        };

        $scope.displayTotal = function() {
            return $scope.orderStatus == 'REVIEW' || $scope.orderStatus == 'CONFIRMED';
        };

        $scope.modifyOrder = function() {
            console.log('submitting order for modification');

            alert('not implemented')
        };

        $scope.reviewOrder = function() {
            console.log('submitting order for review');

            alert('not implemented')
        };

        $scope.confirmOrder = function() {
            console.log('submitting order for confirmation');

            alert('not implemented')
        };





        // Issue the AJAX data load automatically (can be switched on/off)
        $scope.autoLoad = true;

        if ($scope.autoLoad) {
            console.log('auto load (AJAX)');
            if ($scope.orderId) {
                $scope.prepareExistingOrderForm();
            }
            else {
                $scope.prepareNewOrderForm();
            }
        }


    });
