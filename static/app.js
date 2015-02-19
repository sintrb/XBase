var XBase = angular.module('XBase', ['ngRoute', 'ngCookies', 'ui.bootstrap']);

var resturl = '/rest/';

// , ['ngRoute', 'ui.bootstrap']


function initScope($scope, $http){
	$scope.closeAlert = function(){
		$scope.info = null;
	};
	$scope.ajax = function(url ,data, succ, error){
		$scope.doing = true;
		$scope.info = null;
		var ajax = data? $http.post(url, data): $http.get(url);
		ajax.success(function(res){
			$scope.doing = false;
			if(res.succ || typeof(res.succ)=="undefined"){
				if(succ)
					succ(res);
			else if(error)
				error(res.msg);
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
				error('网络错误');
		});
	};
}

function Index($scope, $http, $location, $cookies){
	initScope($scope, $http);
	$scope.$location = $location;
	if(!$cookies.token){
		$location.path('/.login');
	}
	else{
		$scope.ajax(resturl, null,
			function(res){
				$scope.apps = res.apps;
			},
			function(err){
				delete $cookies.token;
				$location.path('/.login');
			});
	}

	$scope.logout = function(){
		delete $cookies.token;
		$location.path('/.login');
	};
}

function Domain($scope, $http, $location, $cookies, $routeParams){
	initScope($scope, $http);
	$scope.$location = $location;
	$scope.domain = $routeParams.domain;

	$scope.ajax(resturl+$scope.domain+"/", null, 
		function(res){
			var keys = [];
			for(var k in res){
				keys.push(k);
			}
			keys.sort();
			$scope.keyvals = [];
			for (var i = 0; i < keys.length; i++) {
				$scope.keyvals.push({
					key:keys[i],
					val:res[keys[i]]
				})
			};
		}
	);
	$scope.delete = function(domain, key){
		console.log(domain + " " + key);
	};
}

function KeyVal($scope, $http, $location, $cookies, $routeParams, $timeout){
	initScope($scope, $http);
	$scope.$location = $location;
	$scope.domain = $routeParams.domain;
	$scope.key = $routeParams.key;
	$scope.keyvalurl = function(){
		return resturl+$scope.domain+"/"+$scope.key;
	};
	$scope.ajax(resturl+$scope.domain+"/"+$scope.key, null, 
		function(res){
			$scope.value = res;
		}
	);

	$scope.save = function(){
		$scope.ajax($scope.keyvalurl(), $scope.value, function(){
			$scope.info = "保存成功";
			$timeout(function(){
				var u = '/'+$scope.domain+"/"+$scope.key;
				if($location.path() != u){
					$location.path(u);
				}
				else{
					$scope.info = null;
				}
			}, 500);
		});
	};
}

function Login($scope, $http, $location, $cookies, $timeout){
	initScope($scope, $http);
	$scope.$location = $location;
	if($cookies.token){
		// $timeout(function(){
			$location.path('/');
		// }, 500);
	}
	$scope.login = function(){
		$scope.ajax('/.login', {
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
	if ($scope.password != $scope.repassword){
			$scope.info = {
				type:'error',
				msg:'两次密码不相等'
			}
		return false;
	}
	$scope.sigin = function(){
		$scope.ajax('/.sigin', {
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
		.when('/.login', {
			controller: Login,
			templateUrl: '/static/login.html'
		})
		.when('/.sigin', {
			controller: Sign,
			templateUrl: '/static/sigin.html'
		})
		.when('/:domain', {
			controller: Domain,
			templateUrl: '/static/domain.html'
		})
		.when('/:domain/:key', {
			controller: KeyVal,
			templateUrl: '/static/keyval.html'
		})
		.otherwise({
			redirectTo: '/'
		});
}



XBase.config(['$routeProvider', routeConfig]);