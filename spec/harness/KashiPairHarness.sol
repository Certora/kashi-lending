pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../contracts/KashiPair.sol";
import "@sushiswap/bentobox-sdk/contracts/IBentoBoxV1.sol";



contract KashiPairHarness is KashiPair {
	constructor() KashiPair(IBentoBoxV1(0)) public {	}

	// for invariants we need a function that simulate the constructor 
	function init_state() public { }

	// getters for internals
	function totalAssetElastic() public returns (uint256) {
		return totalAsset.elastic;
	}

	// totalAssetBase() is already defined in KashiPair.sol with the name totalSupply

	function totalBorrowElastic() public returns (uint256) {
		return totalBorrow.elastic;
	}

	function totalBorrowBase() public returns (uint256) {
		return totalBorrow.base;
	}

    function borrowToElastic(uint256 part) public returns (uint256)  {
        return totalBorrow.toElastic(part, true);
    }

	function accrue() override public { }

	function cook(uint8[] calldata actions, uint256[] calldata values,
				  bytes[] calldata datas) external override payable
				  					  returns (uint256 value1, uint256 value2) {
	}

	function feesEarnedFraction() public returns (uint128) {
		return accrueInfo.feesEarnedFraction;
	}

    function accrueInterest()  public {
       AccrueInfo memory _accrueInfo = accrueInfo;
        // Number of seconds since accrue was called
        uint256 elapsedTime = block.timestamp - _accrueInfo.lastAccrued;
        if (elapsedTime == 0) {
            return;
        }
        _accrueInfo.lastAccrued = uint64(block.timestamp);

        Rebase memory _totalBorrow = totalBorrow;
        if (_totalBorrow.base == 0) {
            // If there are no borrows, reset the interest rate
            if (_accrueInfo.interestPerSecond != STARTING_INTEREST_PER_SECOND) {
                _accrueInfo.interestPerSecond = STARTING_INTEREST_PER_SECOND;
                emit LogAccrue(0, 0, STARTING_INTEREST_PER_SECOND, 0);
            }
            accrueInfo = _accrueInfo;
            return;
        }

        uint256 extraAmount = 0;
        uint256 feeFraction = 0;
        Rebase memory _totalAsset = totalAsset;
        uint256 fullAssetAmount = bentoBox.toAmount(asset, _totalAsset.elastic, false).add(_totalBorrow.elastic);

        // Accrue interest
        extraAmount = uint256(_totalBorrow.elastic).mul(_accrueInfo.interestPerSecond).mul(elapsedTime) / 1e18;
        _totalBorrow.elastic = _totalBorrow.elastic.add(extraAmount.to128());

        uint256 feeAmount = extraAmount.mul(PROTOCOL_FEE) / PROTOCOL_FEE_DIVISOR; // % of interest paid goes to fee
        feeFraction = feeAmount.mul(_totalAsset.base) / fullAssetAmount.sub(feeAmount);
        _accrueInfo.feesEarnedFraction = _accrueInfo.feesEarnedFraction.add(feeFraction.to128());
        totalAsset.base = _totalAsset.base.add(feeFraction.to128());
        totalBorrow = _totalBorrow;
		accrueInfo = _accrueInfo;
    }

}