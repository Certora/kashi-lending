pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "./KashiPairHarnessLIQ.sol";

contract KashiPairHarnessCook is KashiPairHarnessLIQ {


	bool public solventCheckByModifier;
	bool public needsSolvencyCheck;


	modifier solvent() override {
        _;
        require(_isSolvent(msg.sender, false, exchangeRate), "KashiPair: user insolvent");
		solventCheckByModifier = true;
    }


	function cookLight(
        uint8 action      
    ) external virtual payable returns (uint256 value1, uint256 value2) {
        CookStatus memory status;
            if (!status.hasAccrued && action < 10) {
                accrue();
                status.hasAccrued = true;
            }
            if (action == ACTION_ADD_COLLATERAL) {
                //(int256 share, address to, bool skim) = abi.decode(datas[i], (int256, address, bool));
               // addCollateral(to, skim, _num(share, value1, value2));
            } else if (action == ACTION_ADD_ASSET) {
                //(int256 share, address to, bool skim) = abi.decode(datas[i], (int256, address, bool));
              //  value1 = _addAsset(to, skim, _num(share, value1, value2));
            } else if (action == ACTION_REPAY) {
                //(int256 part, address to, bool skim) = abi.decode(datas[i], (int256, address, bool));
              //  _repay(to, skim, _num(part, value1, value2));
            } else if (action == ACTION_REMOVE_ASSET) {
              //  (int256 fraction, address to) = abi.decode(datas[i], (int256, address));
              //  value1 = _removeAsset(to, _num(fraction, value1, value2));
            } else if (action == ACTION_REMOVE_COLLATERAL) {
               // (int256 share, address to) = abi.decode(datas[i], (int256, address));
               // _removeCollateral(to, _num(share, value1, value2));
                needsSolvencyCheck = true;
            } else if (action == ACTION_BORROW) {
               // (int256 amount, address to) = abi.decode(datas[i], (int256, address));
              //  (value1, value2) = _borrow(to, _num(amount, value1, value2));
                needsSolvencyCheck = true;
            } else if (action == ACTION_BENTO_SETAPPROVAL) {
               // (address user, address _masterContract, bool approved, uint8 v, bytes32 r, bytes32 s) =
                //    abi.decode(datas[i], (address, address, bool, uint8, bytes32, bytes32));
               // bentoBox.setMasterContractApproval(user, _masterContract, approved, v, r, s);
            } else if (action == ACTION_BENTO_DEPOSIT) {
               // (value1, value2) = _bentoDeposit(datas[i], values[i], value1, value2);
            } else if (action == ACTION_BENTO_WITHDRAW) {
               // (value1, value2) = _bentoWithdraw(datas[i], value1, value2);
            } else if (action == ACTION_BENTO_TRANSFER) {
               // (IERC20 token, address to, int256 share) = abi.decode(datas[i], (IERC20, address, int256));
               // bentoBox.transfer(token, msg.sender, to, _num(share, value1, value2));
            } else if (action == ACTION_BENTO_TRANSFER_MULTIPLE) {
               // (IERC20 token, address[] memory tos, uint256[] memory shares) = abi.decode(datas[i], (IERC20, address[], uint256[]));
               // bentoBox.transferMultiple(token, msg.sender, tos, shares);
            } else if (action == ACTION_CALL) {
               // (address callee, bytes memory callData, bool useValue1, bool useValue2, uint8 returnValues) =
               //     abi.decode(datas[i], (address, bytes, bool, bool, uint8));
              //  callData = _callData(callData, useValue1, useValue2, value1, value2);
              //  bytes memory returnData = _call(values[i], callee, callData);

              /*  if (returnValues == 1) {
                    (value1) = abi.decode(returnData, (uint256));
                } else if (returnValues == 2) {
                    (value1, value2) = abi.decode(returnData, (uint256, uint256));
                }*/
            } else if (action == ACTION_GET_REPAY_SHARE) {
               /* int256 part = abi.decode(datas[i], (int256));
                value1 = bentoBox.toShare(asset, totalBorrow.toElastic(_num(part, value1, value2), true), true); */
            } else if (action == ACTION_GET_REPAY_PART) {
                /* int256 amount = abi.decode(datas[i], (int256));
                value1 = totalBorrow.toBase(_num(amount, value1, value2), false);*/
            }

        if (needsSolvencyCheck) {
            require(_isSolvent(msg.sender, false, exchangeRate), "KashiPair: user insolvent");
        }
    }

  /*       
	bool public needsSolvencyCheck;
	int256 share; 
	address to; 
	bool skim;
	int256 fraction;
	int256 part;
	int256 amount;
	address user;
	address _masterContract;
	bool approved;
	uint8 v; 
	bytes32 s;
	bytes32 r;
	IERC20 token;
	uint256 value1; uint256 value2;
	address[] memory tos;
	uint256[] memory shares;
	uint256 values;
	bytes data;


	function callACTION_ADD_COLLATERAL() public  {            
        addCollateral(to, skim, _num(share, value1, value2));
	}

    function callACTION_ADD_ASSET() {
        value1 = _addAsset(to, skim, _num(share, value1, value2));
	}

    function callACTION_REPAY() {
         _repay(to, skim, _num(part, value1, value2));
	}

    function callACTION_REMOVE_ASSET() {
        value1 = _removeAsset(to, _num(fraction, value1, value2));
	}

    function callACTION_REMOVE_COLLATERA() {
        _removeCollateral(to, _num(share, value1, value2));
        needsSolvencyCheck = true;
	}
    function callACTION_BORROW() {
        (value1, value2) = _borrow(to, _num(amount, value1, value2));
        needsSolvencyCheck = true;
	}
	function callACTION_BENTO_SETAPPROVAL() {
        bentoBox.setMasterContractApproval(user, _masterContract, approved, v, r, s);
	}

    function callACTION_BENTO_DEPOSIT() {
        (value1, value2) = _bentoDeposit(datas, values, value1, value2);
	}

    function callACTION_BENTO_WITHDRAW() {
        (value1, value2) = _bentoWithdraw(datas[i], value1, value2);
	}

    function call ACTION_BENTO_TRANSFER() {
        bentoBox.transfer(token, msg.sender, to, _num(share, value1, value2));
	}

    function call ACTION_BENTO_TRANSFER_MULTIPLE() {
        bentoBox.transferMultiple(token, msg.sender, tos, shares);
	}
     
    function call ACTION_GET_REPAY_SHARE() {
        value1 = bentoBox.toShare(asset, totalBorrow.toElastic(_num(part, value1, value2), true), true);
	}

    function call ACTION_GET_REPAY_PART() {
        value1 = totalBorrow.toBase(_num(amount, value1, value2), false);
    }

*/





}