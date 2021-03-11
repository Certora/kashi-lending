using DummyERC20A as collateralInstance
using DummyERC20B as assetInstance
using SimpleBentoBox as bentoBox


methods {
	balanceOf(address a) returns (uint256) envfree
	userBorrowPart(address user) returns (uint256) envfree
	totalCollateralShare() returns (uint256) envfree
	userCollateralShare(address user) returns (uint256) envfree
	totalAssetElastic() returns (uint256) envfree
	totalSupply() returns (uint256) envfree
	totalBorrowElastic() returns (uint256) envfree
	totalBorrowBase() returns (uint256) envfree
	borrowToElastic(uint256 part) returns (uint256) envfree
	
	collateralInstance.balanceOf(address a) returns (uint256) envfree
	feesEarnedFraction() returns (uint128) envfree
	collateral() returns (address) envfree
	asset() returns (address) envfree
	feeTo() returns (address) envfree
	isSolvent(address user, bool open) returns (bool) envfree

	// Bentobox functions
	transfer(address token, address from, address to, uint256 share) => DISPATCHER(true)
	bentoBox.balanceOf(address token, address user) returns (uint256) envfree
	bentoBox.toShare(address token, uint256 amount, bool roundUp) returns (uint256) envfree
	bentoBox.toAmount(address token, uint256 share, bool roundUp) returns (uint256) envfree
	
	deposit(address token, address from, address to, uint256 amount, uint256 share) => DISPATCHER(true)
	
	// Swapper
	swap(address fromToken, address toToken, address recipient, uint256 amountToMin, uint256 shareFrom) => DISPATCHER(true)
	swappers(address) => NONDET

	// Weth specific methods
	deposit() => DISPATCHER(true)
	withdraw(uint256 amount) => DISPATCHER(true)
	// ERC20 token method
	transferFrom(address from, address to, uint256 amount) => DISPATCHER(true)
	transfer(address to, uint256 amount) => DISPATCHER(true)

	setUser1(address u1) envfree
	setBorrowPart1(uint256 part1) envfree
	setUser2(address u2) envfree
	setBorrowPart2(uint256 part2) envfree

}


definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;

function validState() {
	require collateralInstance == collateral();
	require assetInstance == asset();

	require ( (totalBorrowBase() > 0) => (totalSupply() > 0) ) &&
	( (totalSupply() == 0) => (totalAssetElastic() == 0) );
	require totalBorrowElastic() >= totalBorrowBase()  && 
	( (totalBorrowElastic() == 0) <=> (totalBorrowBase() == 0) );
	require bentoBox.balanceOf(collateralInstance, currentContract) >= totalCollateralShare();
	require bentoBox.balanceOf(assetInstance, currentContract) >= totalAssetElastic();
	
}

// should only use this for timeouts on the general verison
function RATIO_ONE() {
	require totalBorrowElastic() == totalBorrowBase();
	require totalSupply() ==  totalAssetElastic(); 
}

// RULES


rule balancesChange() {
	validState();
	
	env e;
	uint256 collateralBalanceBefore = bentoBox.balanceOf(collateralInstance, currentContract);
	uint256 assetBalanceBefore = bentoBox.balanceOf(assetInstance, currentContract);
	//need to strength the state: otherwise counter example as the fee paid on the extra is more than the asset gained from liguidation:
	//http://vaas-stg.certora.com/output/23658/b4c3c3e7bb7dbd218f24/?anonymousKey=db3042476c702be7b79b42c3d2dbfd00e99bf265
	require totalAssetElastic() == assetBalanceBefore;
	
	//if msg.sender==curentcontract bad things can happen
	//https://vaas-stg.certora.com/output/23658/f9d8f2525483988d8372/?anonymousKey=b9c2a45b98db7e62a65c32e3f767ef47fd9bb20b
	require e.msg.sender != currentContract;

	//require to!=currentContract - added temporarly
	//require collateralAmount > 0 - added temporarly
	
	calldataarg args;
	liquidate(e, args);
	uint256 collateralBalanceAfter = bentoBox.balanceOf(collateralInstance, currentContract);
	uint256 assetBalanceAfter = bentoBox.balanceOf(assetInstance, currentContract);
	assert (assetBalanceAfter >= assetBalanceBefore,
			"asset balance decreased");
	assert (collateralBalanceAfter <= collateralBalanceBefore,
			"collateral balance increased");
	assert (assetBalanceAfter > assetBalanceBefore) <=> (collateralBalanceAfter < collateralBalanceBefore),
			"only one balance changed";
			
}


//bento ratio 1 : ratio 1 in 
/*
rule addativity(address u1, address u2, uint256 part1, uint256 part2) {
	env e;
	calldataarg argsFirst;
	calldataarg argsSecond;
	validState();
	RATIO_ONE();		
	storage init = lastStorage;

	setUser1(u1);
	setBorrowPart1(part1);
	setUser2(u2);
	setBorrowPart2(part2);	
	
	liquidateFirstUser(e, argsFirst);
	liquidateSecondUser(e, argsSecond);
	 
	
	uint256 collateralBalanceScenario1 = bentoBox.balanceOf(collateralInstance, currentContract);
	uint256 assetBalanceScenario1 = bentoBox.balanceOf(assetInstance, currentContract);
	uint256 totalBorrowElasticScenario1 = totalBorrowElastic();
	uint256 totalBorrowBaseScenario1 = totalBorrowBase();
	uint256 totalSupplyScenario1 = totalSupply();
	uint256 totalAssetElasticScenario1 = totalAssetElastic(); 
	uint256 totalCollateralShareScenario1 = totalCollateralShare();

	calldataarg argsBoth;	
	liquidateTwoTogether(e,argsBoth) at init;
	
	uint256 collateralBalanceScenario2 = bentoBox.balanceOf(collateralInstance, currentContract);
	uint256 assetBalanceScenario2 = bentoBox.balanceOf(assetInstance, currentContract);
	uint256 totalBorrowElasticScenario2 = totalBorrowElastic();
	uint256 totalBorrowBaseScenario2 = totalBorrowBase();
	uint256 totalSupplyScenario2 = totalSupply();
	uint256 totalAssetElasticScenario2 = totalAssetElastic(); 
	uint256 totalCollateralShareScenario2 = totalCollateralShare();

	assert 	collateralBalanceScenario1 == collateralBalanceScenario2 &&
			assetBalanceScenario1 == assetBalanceScenario2 &&
			totalBorrowElasticScenario1 == totalBorrowElasticScenario2 &&
			totalBorrowBaseScenario1 == totalBorrowBaseScenario2 &&
			totalSupplyScenario1 == totalSupplyScenario2 &&
			totalAssetElasticScenario1 == totalAssetElasticScenario2 &&
			totalCollateralShareScenario1 == totalCollateralShareScenario2;
			
}
*/