pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "./KashiPairHarnessFlat.sol";

contract KashiPairHarnessNOLIQ is KashiPairHarnessFlat {
	function liquidate(address[] calldata users, uint256[] calldata borrowParts,
	 				   address to, ISwapper swapper, bool open) override public { }
}