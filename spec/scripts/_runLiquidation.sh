certoraRun.py spec/harness/KashiPairHarnessLIQ.sol spec/harness/DummyERC20A.sol \
	spec/harness/DummyERC20B.sol  spec/harness/WhitelistedSwapper.sol spec/harness/Swapper.sol spec/harness/SimpleBentoBox.sol contracts/mocks/OracleMock.sol spec/harness/DummyWeth.sol \
	--link KashiPairHarnessLIQ:collateral=DummyERC20A KashiPairHarnessLIQ:asset=DummyERC20B KashiPairHarnessLIQ:bentoBox=SimpleBentoBox KashiPairHarnessLIQ:oracle=OracleMock  KashiPairHarnessLIQ:masterContract=KashiPairHarnessLIQ KashiPairHarnessLIQ:whitelistedSwapper=WhitelistedSwapper KashiPairHarnessLIQ:redSwapper=Swapper \
	--solc solc6.12 \
	--settings -copyLoopUnroll=4,-b=1,-ignoreViewFunctions,-assumeUnwindCond \
	--verify KashiPairHarnessLIQ:spec/liquidate.spec \
	--staging \
	--cache KashiPairHarnessLIQ \
	--msg "KashiPairHarnessLIQ - liquidate.spec $1"  