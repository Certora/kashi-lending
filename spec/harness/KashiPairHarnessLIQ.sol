pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "./KashiPairHarness.sol";

contract KashiPairHarnessLIQ is KashiPairHarness {
	mapping(address => bool) public closeSolvent;
	mapping(address => bool) public openSolvent;

	function _isSolvent(address user, bool open, uint256 _exchangeRate) internal override view returns (bool) {
        if (closeSolvent[user]) {
			return true;
		}
		
		return open && openSolvent[user];
    }

	mapping (uint256 => uint16) public fee;
	function computeFee(uint256 amount) internal override returns (uint256) {
		if (amount == 0)
			return 0;
		require (fee[amount] < amount );
        return uint256(fee[amount]); // % of profit goes to fee
    }

	mapping (uint256 => mapping( uint256 => uint256)) public collateralNeed;
	function computeCollateral(uint256 borrowAmount, uint256 _exchangeRate) internal override returns (uint256) {
		if (borrowAmount ==0)
			return 0;
		require(collateralNeed[borrowAmount][_exchangeRate] > 0);
        return collateralNeed[borrowAmount][_exchangeRate] ;
    }

	ISwapper whitelistedSwapper;
	ISwapper redSwapper;


	function liquidate(
        address[] calldata users,
        uint256[] calldata borrowParts,
        address to,
        ISwapper swapper,
        bool open
    )  public override {
		// if collateral is transferred to this, then bentoBox.balanceOf(collateral, this) does not decrease
		require( to != address(this)); 
		if(open) {
        	require (swapper == whitelistedSwapper );
		}
		else {
			require (swapper == redSwapper );
		}
		super.liquidate(users, borrowParts, to, swapper, open);

	}

	address public user1;
	address public user2;
	uint256 public borrowPart1;
	uint256 public borrowPart2;
	
	function setUser1(address u) public {
		user1 = u;
	}

	function setUser2(address u) public {
		user2 = u;
	}

	function setBorrowPart1(uint256 p) public {
		borrowPart1 = p;
	}
	
	function setBorrowPart2(uint256 p) public {
		borrowPart2 = p;
	}
/*
	function liquidateFirstUser(
        address[] calldata users,
        uint256[] calldata borrowParts,
        address to,
        ISwapper swapper,
        bool open
    )  public  {
		// if collateral is transferred to this, then bentoBox.balanceOf(collateral, this) does not decrease
		require( to != address(this)); 
		require( users.length == 1);
		require( users[0] == user1 );
		require( borrowParts[0] == borrowPart1 );
		if(open) {
        	require (swapper == whitelistedSwapper );
		}
		else {
			require (swapper == redSwapper );
		}
		super.liquidate(users, borrowParts, to, swapper, open);

	}

	function liquidateSecondUser(
        address[] calldata users,
        uint256[] calldata borrowParts,
        address to,
        ISwapper swapper,
        bool open
    )  public  {
		// if collateral is transferred to this, then bentoBox.balanceOf(collateral, this) does not decrease
		require( to != address(this)); 
		require( users.length == 1);
		require( users[0] == user2 );
		require( borrowParts[0] == borrowPart2 );
		if(open) {
        	require (swapper == whitelistedSwapper );
		}
		else {
			require (swapper == redSwapper );
		}
		super.liquidate(users, borrowParts, to, swapper, open);

	}

	function liquidateTwoTogether(
        address[] calldata users,
        uint256[] calldata borrowParts,
        address to,
        ISwapper swapper,
        bool open
    )  public  {
		// if collateral is transferred to this, then bentoBox.balanceOf(collateral, this) does not decrease
		require( to != address(this)); 
		require( users.length == 2);
		require( users[0] == user1 );
		require( users[1] == user2 );
		require( borrowParts[0] == borrowPart1 );
		require( borrowParts[1] == borrowPart2 );
		if(open) {
        	require (swapper == whitelistedSwapper );
		}
		else {
			require (swapper == redSwapper );
		}
		super.liquidate(users, borrowParts, to, swapper, open);

	}
*/


}