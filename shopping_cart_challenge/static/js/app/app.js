app = angular.module("ShoppingCartChallenge", []);

app.controller("OrderController", function($scope, $http) {
        // behavior altering flag (for dev purposes)
        $scope.autoLoad = true;

        $scope.products = null;
        $scope.ajaxError = null;

        $scope.loadNewOrder = function() {
            var promise = $http.get("/api/products");
            promise.success(function(data, status, headers, config) {
                $scope.products = [];
                for (var i=0; i<data.length; i++) {
                    var product = data[i];
                    var product_wrapper = {};
                    product_wrapper.name = product.name;
                    product_wrapper.price = product.price;
                    product_wrapper.check = false;
                    product_wrapper.quantity = null;

                    $scope.products.push(product_wrapper)
                }

                $scope.ajaxError = null;
            });
            promise.error(function(data, status, headers, config) {
                $scope.products = null;
                $scope.ajaxError = 'Could not load list of products (AJAX call failed)';
            });
        };

        if ($scope.autoLoad) {
            console.log('auto load (AJAX)');
            $scope.loadNewOrder();
        }

        $scope.reviewOrder = function() {
            console.log('submitting order for review')

        }


    });
