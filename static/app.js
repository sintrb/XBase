var XBase = angular.module('XBase', ['ngRoute', 'ngCookies', 'ui.bootstrap']);


// , ['ngRoute', 'ui.bootstrap']


function initScope($scope){

}

function Index($scope, $http, $location, $cookies){
	$scope.$location = $location;
	if(!$cookies.username){
		$location.path('/login');
	};
	$scope.logout = function(){
		// $cookies.username = '';
		$location.path('/login');
	};
}

function Login($scope, $http, $location){
	$scope.$location = $location;
	$scope.closeAlert = function(){
		$scope.info = null;
	}
	$scope.login = function(){
		$scope.doing = true;
		$http.post('/.login', {
			username: $scope.username,
			password: $scope.password
		})
		.success(function(res){
			$scope.doing = false;
			if(res.succ){
				$location.path('/');
			}
			else{
				$scope.info = {
					type:'error',
					msg:res.msg
				};
			}
			console.log(res);
		})
		.error(function(){
			$scope.doing = false;
			$scope.info = {
				type:'error',
				msg:'网络错误'
			}
		});
	}
}

function Sign($scope, $http, $location){
	$scope.$location = $location;
	$scope.sigin = function(){
		$scope.doing = true;
		$http.post('/.sigin', {
			username: $scope.username,
			password: $scope.password
		})
		.success(function(res){
			$scope.doing = false;
			if(res.succ){
				$location.path('/');
			}
			else{
				$scope.info = {
					type:'error',
					msg:res.msg
				};
			}
			console.log(res);
		})
		.error(function(){
			$scope.doing = false;
			$scope.info = {
				type:'error',
				msg:'网络错误'
			}
		});
	}
}

function routeConfig($routeProvider) {
	$routeProvider
		.when('/', {
			controller: Index,
			templateUrl: '/static/main.html'
		})
		.when('/login', {
			controller: Login,
			templateUrl: '/static/login.html'
		})
		.when('/sigin', {
			controller: Sign,
			templateUrl: '/static/sigin.html'
		})
		.otherwise({
			redirectTo: '/'
		});
}



XBase.config(['$routeProvider', routeConfig]);