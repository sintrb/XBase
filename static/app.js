var XBase = angular.module('XBase', ['ngRoute', 'ngCookies', 'ui.bootstrap']);


// , ['ngRoute', 'ui.bootstrap']


function initScope($scope, $http){
	$scope.closeAlert = function(){
		$scope.info = null;
	};
	$scope.post = function(url ,data, succ, error){
		$scope.doing = true;
		$scope.info = null;
		$http.post(url, data)
		.success(function(res){
			$scope.doing = false;
			if(res.succ){
				if(succ)
					succ(res);
			}
			else{
				$scope.info = {
					type:'error',
					msg:res.msg
				};
			}
		})
		.error(function(){
			$scope.doing = false;
			$scope.info = {
				type:'error',
				msg:'网络错误'
			}
			if(error)
				error();
		});
	};
}

function Index($scope, $http, $location, $cookies){
	initScope($scope, $http);
	$scope.$location = $location;
	if(!$cookies.token){
		$location.path('/login');
	};
	$scope.logout = function(){
		delete $cookies.token;
		$location.path('/login');
	};
}

function Login($scope, $http, $location, $timeout){
	initScope($scope, $http);
	$scope.$location = $location;
	$scope.login = function(){
		$scope.post('/.login', {
			username: $scope.username,
			password: $scope.password
			},
			function(res){
				$scope.info = "登录成功";
				$timeout(function(){
					$location.path('/');
				}, 500);
			}
		);
	}
}

function Sign($scope, $http, $location, $timeout){
	initScope($scope, $http);
	$scope.$location = $location;
	$scope.sigin = function(){
		$scope.post('/.sigin', {
			username: $scope.username,
			password: $scope.password
			},
			function(res){
				$scope.info = "注册成功";
				$timeout(function(){
					$location.path('/');
				}, 500);
			}
		);
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