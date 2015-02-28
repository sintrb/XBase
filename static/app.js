var XBase = angular.module('XBase', ['ngRoute', 'ngCookies', 'ui.bootstrap']);

var resturl = '/api/';

Array.prototype.removeat = function(dx){
	if(isNaN(dx)||dx>this.length){return false;}
	this.splice(dx,1);
	return this;
};

Array.prototype.remove = function(obj){
	var dx = this.indexOf(obj);
	if(dx>=0){
		this.removeat(dx);
	}
	return this;
}

// , ['ngRoute', 'ui.bootstrap']


function initScope($scope, $http, $timeout){
	$scope.closeAlert = function(){
		$scope.info = null;
	};
	$scope.ajax = function(req, succ, error){
		var defreq = {
			method:'GET',
		}
		if(typeof(req)=="string"){
			req = {
				url: req
			};
		}
		if(typeof(req.method) == "undefined" && typeof(req.data) != "undefined"){
			req.method = "POST";
		}
		for(var mn in defreq){
			if(typeof(req[mn])=="undefined"){
				req[mn] = defreq[mn];
			}
		}
		var ajax = null;
		switch(req.method){
			case 'GET':
			ajax = $http.get(req.url);
			break;
			case 'POST':
			ajax = $http.post(req.url, req.data);
			break;
			case 'DELETE':
			ajax = $http.delete(req.url, req.data);
			break;
		}
		$scope.doing = true;
		$scope.info = null;
		ajax.success(function(res){
			$scope.doing = false;
			if(res.succ || typeof(res.succ)=="undefined"){
				if(succ)
					succ(res);
			}
			else{
				if(typeof(res.msg)!="undefined"){
					$scope.info = {
						type:'error',
						msg:res.msg
					};
				}
				if(error){
					error(res);
				}
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

		$scope.delayinfo = function(info, delay, cbk){
			if(typeof(delay) == "function"){
				cbk = delay;
				delay = 0;
			}
			if(!delay){
				delay = 500;
			}
			$scope.info = info;
			$timeout(function(){
				$scope.info = null;
				if(cbk)
					cbk();
			}, delay);
		}
	}
}

function Index($scope, $http, $location, $cookies, $timeout){
	initScope($scope, $http, $timeout);
	$scope.$location = $location;
	if(!$cookies.token){
		$location.path('/.login');
	}
	else{
		$scope.ajax(resturl,
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

	$scope.apptemp = 'app';
	$scope.add = function(){
		var name = prompt("输入应用名称", $scope.apptemp);
		var has = false;
		if(!name)
			return;
		$scope.apptemp = name;
		$.each($scope.apps, function(index, val) {
			if(val.name == name){
				has = true;
			}
		});
		if(has){
			$scope.info = {
				type:'error',
				msg:'已经存在该应用'
			};
			return;
		}
		if(name.length>0 && name!='.' && name!='/'){
			$scope.ajax(
				{
					url:resturl+name,
					method:"POST"
				},
				function(res){
					$scope.apps.push(res.app);
					$scope.delayinfo("添加成功!", function(){
						$location.path('/'+res.app.name);
					});
				}
			);
		}
		else{
			$scope.info = {
				type:'error',
				msg:'应用名称不对'
			};
		}
	}

	$scope.delete = function(app){
		if(confirm("确定删除["+app.name+"]")){
			$scope.ajax(
				{
					url:resturl+app.name+"/",
					method:"DELETE"
				},
				function(){
					$scope.info = "删除成功";
					$scope.apps.remove(app);
					$timeout(function(){
						$scope.info = null;
					}, 500);
				}
			);
		}
	}
}

function Domain($scope, $http, $location, $cookies, $routeParams, $timeout){
	initScope($scope, $http, $timeout);
	$scope.$location = $location;
	$scope.domain = $routeParams.domain;

	$scope.ajax(resturl+$scope.domain+"/", 
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
	$scope.add = function(){
		$location.path($scope.domain+'/.key');
	}
	$scope.delete = function(kv){
		if(confirm("确定删除["+kv.key+"]")){
			$scope.ajax(
				{
					url:resturl+$scope.domain+"/"+kv.key,
					method:"DELETE"
				},
				function(){
					$scope.info = "删除成功";
					$scope.keyvals.remove(kv);
					$timeout(function(){
						$scope.info = null;
					}, 500);
				}
			);
		}
	};
}

function KeyVal($scope, $http, $location, $cookies, $routeParams, $timeout){
	initScope($scope, $http, $timeout);
	$scope.$location = $location;
	$scope.domain = $routeParams.domain;
	$scope.key = $routeParams.key;
	
	$scope.keyvalurl = function(){
		return resturl+$scope.domain+"/"+$scope.key;
	};

	if($scope.key==".key"){
		$scope.key = "";
	}
	else{
		$scope.ajax(resturl+$scope.domain+"/"+$scope.key, 
			function(res){
				$scope.value = res;
			}
		);
	}

	$scope.save = function(){
		$scope.ajax(
			{
				url:$scope.keyvalurl(),
				data:$scope.value,
			},
			function(){
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
			}
		);
	};
}

function Login($scope, $http, $location, $cookies, $timeout){
	initScope($scope, $http, $timeout);
	$scope.$location = $location;
	if($cookies.token){
		// $timeout(function(){
			$location.path('/');
		// }, 500);
	}
	$scope.login = function(){
		$scope.ajax(
			{
				url:'/.login',
				data:{
					username: $scope.username,
					password: $scope.password
				},
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
	initScope($scope, $http, $timeout);
	$scope.$location = $location;
	$scope.sigin = function(){
		if ($scope.password != $scope.repassword){
				$scope.info = {
					type:'error',
					msg:'两次密码不相等'
				}
			return false;
		}
		
		$scope.ajax({
				url:'/.sigin',
				data:{
				username: $scope.username,
				password: $scope.password
				}
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