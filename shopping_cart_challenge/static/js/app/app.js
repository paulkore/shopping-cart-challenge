appModule = angular.module("ShoppingCartChallenge", []);

appModule.controller("OrderController", function($scope, $location, $http) {
        // behavior altering flag (for dev purposes)
        $scope.autoLoad = true;

        $scope.orderId = null;
        $scope.formTitle = 'New order';

        $scope.url = $location.absUrl();
        console.log('url = ' + $scope.url);
        if (!$scope.url.contains('orders/new')) {
            // TODO: this is still error prone
            var numericValues = $scope.url.match( /\d+/g);
            $scope.orderId = Number(numericValues.last());
            $scope.formTitle = 'Edit order';
        }

        $scope.products = null;
        $scope.ajaxError = null;

        $scope.loadEmptyOrder = function() {
            console.log('loading data for empty order');

            var promise = $http.get("/api/products");
            promise.success(function(data) {
                $scope.products = [];
                for (var i=0; i<data.length; i++) {
                    var product_data = data[i];
                    var product = {};
                    product.id = product_data.id;
                    product.name = product_data.name;
                    product.price = product_data.price;
                    product.check = false;
                    product.quantity = null;

                    $scope.products.push(product)
                }

                $scope.ajaxError = null;
            });
            promise.error(function(data) {
                $scope.products = null;
                $scope.ajaxError = 'Could not load data (AJAX call failed)';
            });

            return promise;
        };

        $scope.loadExistingOrder = function() {
            console.log('loading data for existing order: ' + $scope.orderId);

            console.log('first, load empty order template');
            $scope.loadEmptyOrder().then(function() {
                if ($scope.ajaxError) {
                    return;
                }

                var promise = $http.get("/api/orders/" + $scope.orderId);
                promise.success(function(data) {
                    var product_quantity_list = data.products;
                    for (var i=0; i<product_quantity_list.length; i++) {
                        var product_quantity_data = product_quantity_list[i];
                        var product_data = product_quantity_data.product;

                        var product = $scope.findProduct(product_data.id);
                        if (product) {
                            product.quantity = product_quantity_data.quantity;
                            product.check = product_quantity_data.quantity > 0;
                        }
                    }

                    $scope.ajaxError = null;
                });
                promise.error(function(data) {
                    $scope.products = null;
                    $scope.ajaxError = 'Could not load data (AJAX call failed)';
                });
            });

        };

        $scope.findProduct = function(product_id) {
            if (!$scope.products) {
                return;
            }

            // TODO: sequential search... not ideal, but it will do for now.
            for (var i=0; i<$scope.products.length; i++) {
                var product = $scope.products[i];
                if (product.id === product_id) {
                    return product;
                }
            }

            return null;
        };

        $scope.reviewOrder = function() {
            console.log('submitting order for review');

            alert('not implemented')
        };




        // auto-load (if enabled)
        if ($scope.autoLoad) {
            console.log('auto load (AJAX)');
            if ($scope.orderId) {
                $scope.loadExistingOrder();
            }
            else {
                $scope.loadEmptyOrder();
            }
        }


    });
