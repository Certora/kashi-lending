certoraRun.py spec/harness/KashiPairHarnessCook.sol spec/harness/DummyERC20A.sol \
	spec/harness/DummyERC20B.sol spec/harness/Swapper.sol spec/harness/SimpleBentoBox.sol contracts/mocks/OracleMock.sol spec/harness/WhitelistedSwapper.sol spec/harness/DummyWeth.sol \
	--link KashiPairHarnessCook:collateral=DummyERC20A KashiPairHarnessCook:asset=DummyERC20B KashiPairHarnessCook:bentoBox=SimpleBentoBox KashiPairHarnessCook:oracle=OracleMock  KashiPairHarnessCook:masterContract=KashiPairHarnessCook KashiPairHarnessCook:whitelistedSwapper=WhitelistedSwapper KashiPairHarnessCook:redSwapper=Swapper \
	--solc solc6.12 \
	--settings -copyLoopUnroll=4,-b=1,-ignoreViewFunctions,-enableStorageAnalysis=true,-assumeUnwindCond \
	--verify KashiPairHarnessCook:spec/kashiPairCook.spec \
	--staging  \
	--cache KashiPairHarnessCook \
	--msg "KashiPairHarnessCook  : $1 "  \