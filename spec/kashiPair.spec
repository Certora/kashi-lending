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
	bentoBox.transfer(address token, address from, address to, uint256 share) => DISPATCHER(true)
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
}

function setup() {
	require collateralInstance == collateral();
	require assetInstance == asset();
}

definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
	
// represents the sum of userCollateralShare[a] for all addresses a
ghost userCollateralSum() returns uint256 {
    init_state axiom userCollateralSum() == 0;
}

// represents the sum of balanceOf[a] for all addresses a
ghost userBalanceOfSum() returns uint256 {
    init_state axiom userBalanceOfSum() == 0;
}

// represents the sum of userBorrowPart[a] for all addresses a
ghost userBorrowSum() returns uint256 {
    init_state axiom userBorrowSum() == 0;
}

// update userCollateralSum on every assginment to userCollateralShare
hook Sstore /* (slot 14) */ userCollateralShare [KEY uint a] uint share (uint oldShare) STORAGE {
	havoc userCollateralSum assuming userCollateralSum@new() == userCollateralSum@old() + share - oldShare; 
}

// when loading userCollateralShare[a] assume that the sum is more than the loaded value
hook Sload uint256 share userCollateralShare[KEY uint a] STORAGE { 
	require userCollateralSum() >= share;
}

// update userBalanceOfSum on every assginment to balanceOf
hook Sstore /* (slot 6) */ balanceOf [KEY uint a] uint balance (uint oldBalance) STORAGE {
	havoc userBalanceOfSum assuming userBalanceOfSum@new() == userBalanceOfSum@old() + balance - oldBalance; 
}

// when loading balanceOf[a] assume that the sum is more than the loaded value
hook Sload uint256 b balanceOf[KEY uint a] STORAGE { 
	require userBalanceOfSum() >= b;
}

// update userBorrowSum on every assginment to balanceOf
hook Sstore /* (slot 15) */ userBorrowPart [KEY uint a] uint part (uint oldPart) STORAGE {
	havoc userBorrowSum assuming userBorrowSum@new() == userBorrowSum@old() + part - oldPart &&userBorrowSum@old() >= oldPart; 
}
// when loading userBorrowPart[a] assume that the sum is more than the loaded value
hook Sload uint256 part userBorrowPart[KEY uint a] STORAGE { 
	require userBorrowSum() >= part;
}

// INVARIANTS

invariant totalCollateralEqUserCollateralSum()
	userCollateralSum() == totalCollateralShare()

invariant totalSupplyEqUserBalanceOfSum()
	userBalanceOfSum() + feesEarnedFraction() == totalSupply() {

		//issue with packing 
		preserved init(bytes b) with (env e) {
			require feesEarnedFraction()==0;
		}
	}

invariant totalBorrowEqUserBorrowSum()
	userBorrowSum() == totalBorrowBase()

invariant validityOfTotalSupply()
	((totalBorrowBase() > 0) => (totalSupply() > 0)) &&
	((totalSupply() == 0) => (totalAssetElastic() == 0))

invariant integrityOfZeroBorrowAssets()
	totalBorrowElastic() >= totalBorrowBase() && 
	((totalBorrowElastic() == 0) <=> (totalBorrowBase() == 0)) {

		preserved repay(address to, bool skim, uint256 amount) with (env e) {
			require totalBorrowElastic() == borrowToElastic(totalBorrowBase());
		}

		preserved liquidate(address[] users, uint256[] amounts, address to, address swap, bool open) with (env e){
			require totalBorrowElastic() == borrowToElastic(totalBorrowBase());
		}


	}

// INVARIANTS implemented as rules

rule totalCollateralLeBentoBoxBalanceOf(method f) { // Le: less than or equal to
	setup();
	require bentoBox.balanceOf(collateralInstance, currentContract) >= totalCollateralShare();  
	env e;
	calldataarg args;
	require e.msg.sender != currentContract;
	f(e,args);
	assert bentoBox.balanceOf(collateralInstance, currentContract) >= totalCollateralShare(); 
}

rule totalAssetElasticLeBentoBoxBalanceOf(method f) { // Le: less than or equal to
	setup();
	require bentoBox.balanceOf(assetInstance, currentContract) >= totalAssetElastic();  
	env e;
	calldataarg args;
	require e.msg.sender != currentContract;
	f(e,args);
	assert bentoBox.balanceOf(assetInstance, currentContract) >= totalAssetElastic(); 
}

function validState() {
	setup();

	requireInvariant validityOfTotalSupply();
	requireInvariant integrityOfZeroBorrowAssets();

	// rule totalCollateralLeBentoBoxBalanceOf
	require bentoBox.balanceOf(collateralInstance, currentContract) >= totalCollateralShare();
	// rule totalAssetElasticLeBentoBoxBalanceOf
	require bentoBox.balanceOf(assetInstance, currentContract) >= totalAssetElastic();
}

/*
rule validStateAsRule(method f) {
	require collateralInstance == collateral();
	require assetInstance == asset();

	requireInvariant validityOfTotalSupply();
	requireInvariant integrityOfZeroBorrowAssets();
	// rule totalCollateralLeBentoBoxBalanceOf
	require bentoBox.balanceOf(collateralInstance, currentContract) >= totalCollateralShare();
	// rule totalAssetElasticLeBentoBoxBalanceOf
	require bentoBox.balanceOf(assetInstance, currentContract) >= totalAssetElastic();
	env e;
	calldataarg args;
	require e.msg.sender != currentContract;
	f(e,args);
	assert bentoBox.balanceOf(assetInstance, currentContract) >= totalAssetElastic(),"1";
	assert bentoBox.balanceOf(collateralInstance, currentContract) >= totalCollateralShare(),"2";
	assert ( (totalBorrowBase() > 0) => (totalSupply() > 0) ) &&
	( (totalSupply() == 0) => (totalAssetElastic() == 0) ), "3";

	assert 	totalBorrowElastic() >= totalBorrowBase()  && 
	( (totalBorrowElastic() == 0) <=> (totalBorrowBase() == 0) ), "4";

}
*/

// RULES

rule noChangeToOthersBorrowAsset(method f, address other) {
	validState();
	env e;

	require other != e.msg.sender;

	uint256 _othersBorrowAsset = userBorrowPart(other);
	
	calldataarg args;
	f(e, args);

	uint256 othersBorrowAsset_ = userBorrowPart(other);
	
	assert (_othersBorrowAsset >= othersBorrowAsset_,
			"other's borrow part changed");
}

// balanceOf should only decrease when we try to call removeAsset
rule noChangeToOthersAssetFraction(address from, address to, address other,
								   uint256 amount, uint256 share, bool skim,
								   method f) {
	validState();

	require other != from;

	uint256 _othersAssetFraction = balanceOf(other);

	// other != msg.sender inside callFunctionWithParams
	// might want to remove this method, it can be confusing for some people
	callFunctionWithParams(from, to, other, amount, share, skim, f); // Work with Nurit to handle withdrawFees!

	uint256 othersAssetFraction_ = balanceOf(other);

	// should I include f.selector == addAsset, transfer, or transferFrom
	// (logically doesn't matter because to is only limited in those cases)
	if (other == to || other == feeTo() ) { 
		assert (_othersAssetFraction <= othersAssetFraction_, 
				"other's asset fraction changed");
	} else {
		assert (_othersAssetFraction == othersAssetFraction_,
				"other's asset fraction changed");
	}
}

rule noChangeToOthersCollateralShare(address other, address to, bool skim,
								     uint256 share, method f) {
	validState();
	env e;

	require other != e.msg.sender; 

	uint256 _othersCollateralShare = userCollateralShare(other);

	if (f.selector == addCollateral(address, bool, uint256).selector) {
		addCollateral(e, to, skim, share);
	} else if (f.selector != liquidate(address[],uint256[],address,address,bool).selector) {
		calldataarg args;
		f(e, args);
	}
	
	uint256 othersCollateralShare_ = userCollateralShare(other);

	// in case of liquidate its fine to reduce the collateral share, work with Nurit to handle liquidate
	if (other == to) { // f.selector == addCollateral(address, bool, uint256).selector && should I include this? (logically doesn't matter)
		assert (_othersCollateralShare <= othersCollateralShare_, 
				"other's collateral share changed");
	} else {
		assert (_othersCollateralShare == othersCollateralShare_,
				"other's collateral share changed");
	}
}

rule integrityOfSkimAddCollateral(address to, uint256 share){
	validState();
	// need two differnet env since they are calling different contracts
	env e;
	env eBento;
	uint256 _collateralShare = userCollateralShare(to);
	uint256 _totalCollateralShare = totalCollateralShare();

	require eBento.msg.sender == e.msg.sender;
	require eBento.block.number == e.block.number;
	require eBento.block.timestamp == e.block.timestamp;
	require e.msg.value == 0;
	require e.msg.sender != currentContract && e.msg.sender != bentoBox;
	//require _collateralShare + share <= MAX_UINT256();

	require  bentoBox.balanceOf(collateralInstance, currentContract) ==  _totalCollateralShare; 
	require  _collateralShare <= _totalCollateralShare;

	//just to get a nice coutner exmple
	//require _totalCollateralShare < 100;
	address from;
	require from == e.msg.sender;
	//transfer shares to lendingPair account in BentoBox 
	sinvoke bentoBox.transfer(eBento, collateralInstance, from, currentContract, share);
	// check if add colalteral is sucessfull
	bool skim = true;
	addCollateral@withrevert(e, to, skim, share);
	uint256 collateralShare_ = userCollateralShare(to);
	bool successful = !lastReverted;
	assert successful && collateralShare_ == _collateralShare + share;
}

// total assets of the lending pair and balance of a user 
// should not change if they deposit and withdraw the same fraction.
rule addThenRemoveAsset(address to, bool skim, uint256 share, uint256 totalAssetElasticAfterAdd) {
	validState();
	env e;

	// skim = false, to test a simple case first
	// skim is true, then maybe we add more assets, so we might want to change == to <=
	require e.msg.sender == to && skim == false; 

	uint256 _totalAssetElastic = totalAssetElastic(); // free shares of LendingPair in BentoBox
	uint256 _totalAssetBase = totalSupply(); // Sum of all users' fraction.
	uint256 _balanceOf = balanceOf(to); // user fraction

	require _totalAssetElastic == 0 <=> _totalAssetBase == 0; // TODO: invariant 
	
	// might want to try doing this in two lines, and manually converting 
	// share to fraction and then calling removeAsset with the converted fraction
	// might also want to compare the return values after proper conversion
    uint256 fraction = addAsset(e, to, skim, share);
	uint256 tempTotalAssetElastic = totalAssetElastic();
	require totalAssetElasticAfterAdd == totalAssetElastic();
	uint256 tempShare = removeAsset(e, to, fraction);
	

	uint256 totalAssetElastic_ = totalAssetElastic();
	uint256 totalAssetBase_ = totalSupply();
	uint256 balanceOf_ = balanceOf(to);
	
	assert (_totalAssetBase == totalAssetBase_, 
			"total asset base changed");

	assert (_balanceOf == balanceOf_, 
			"balance of user changed");

	// totalAssetElastic_ increases by share when assets are added, but
	// it doesn't decrease when assets are removed.
	// not exactly sure what's going on here. (might be a bug)
	//total asset change in favor of the system
	assert (_totalAssetElastic <= totalAssetElastic_, 
			"total asset elastic decreses");
}

// totalCollateralShare and userCollateralShare shouldn't change if we add 
// "x" share worth of collateral then remove "x" share worth of collateral
rule addThenRemoveCollateral(address to, bool skim, uint256 share) {
	validState();
	env e;

	// should something different happen in the case when skim = true?
	require e.msg.sender == to && to != 0; 

	uint256 _totalCollateralShare = totalCollateralShare();
	uint256 _userCollateralShare = userCollateralShare(to); 

	addCollateral(e, to, skim, share);
	
	removeCollateral(e, to, share);

	uint256 totalCollateralShare_ = totalCollateralShare();
	uint256 userCollateralShare_ = userCollateralShare(to);

	//assert(solvent => succeddToRemove, "can not remove collateral");
	assert (_totalCollateralShare == totalCollateralShare_, 
			"total asset base changed");

	assert (_userCollateralShare == userCollateralShare_, 
			"balance of user changed");
}

// total borrow and the borrow part of a user should stay the same 
// if they borrow and repay the same amount
// work in progress ...
rule borrowThenRepay(address to, bool skim, uint256 amount) {
	validState();
	env e;

	// skim = false, to test a simple case first
	// skim is true, then maybe we can repay less?
	require e.msg.sender == to && skim == false && to != 0; 

	// totalAssetElastic()/free shares of LendingPair in BentoBox should also stay the same? totalAssetBase same also?
	uint256 _totalBorrowElastic = totalBorrowElastic();
	uint256 _totalBorrowBase = totalBorrowBase(); // not sure about this
	uint256 _userBorrowPart = userBorrowPart(to); // user's borrow part

	// might also want to compare the return values after proper conversion
	uint256 part;
	uint256 share;
	part, share = borrow(e, to, amount);
	repay(e, to, skim, part);
	
	uint256 totalBorrowElastic_ = totalBorrowElastic();
	uint256 totalBorrowBase_ = totalBorrowBase();
	uint256 userBorrowPart_ = userBorrowPart(to);

	assert (_userBorrowPart == userBorrowPart_, 
			"user borrow part changed");

	// rounding should be in favor of system 
	assert (_totalBorrowElastic >= totalBorrowElastic_, 
			"total borrow elastic changed");

	assert (_totalBorrowBase == totalBorrowBase_, 
			"total borrow base changed");
}


rule solvetCloseIsSolventOpen(address user) {
	validState();
	uint256 totalBorrowBase_ = totalBorrowBase(); // not sure about this
	uint256 totalCollateralShare_ = totalCollateralShare();
	require userCollateralShare(user) <= totalCollateralShare_;
	require userBorrowPart(user) <= totalBorrowBase_;
	assert isSolvent(user, false) => isSolvent(user, true), "close solvent is not open solvent" ;
}

rule solventUser(address user, bool open, method f) {
	validState();
	require isSolvent(user, open);
	env e;
	calldataarg args;
	f(e, args);
	assert isSolvent(user, open), "by perfomring an operation reached an insolvent state";
}

// Helper Functions

// easy to use dispatcher (currently only being used by noChangeToOthersAssetFraction)
// WARNING: Be careful if you limit one of the parameters, it can be limited for 
// many functions.
function callFunctionWithParams(address from, address to, address other, 
								uint256 amount, uint256 share, bool skim,
								method f) {
	env e;

	require other != e.msg.sender;

	if (f.selector == addAsset(address, bool, uint256).selector) {
		addAsset(e, to, skim, share);
	} else if (f.selector == transferFrom(address, address, uint256).selector) {
		transferFrom(e, from, to, amount); 
	} else if  (f.selector == transfer(address, uint256).selector) {
		transfer(e, to, amount); // IERC20 function
	} else {
		calldataarg args;
		f(e,args);
	}
}
