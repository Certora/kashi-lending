certoraRun.py spec/harness/KashiPairHarness.sol spec/harness/DummyERC20A.sol \
	spec/harness/DummyERC20B.sol spec/harness/Swapper.sol spec/harness/SimpleBentoBox.sol contracts/mocks/OracleMock.sol spec/harness/DummyWeth.sol spec/harness/WhitelistedSwapper.sol \
	--link KashiPairHarness:collateral=DummyERC20A KashiPairHarness:asset=DummyERC20B KashiPairHarness:bentoBox=SimpleBentoBox KashiPairHarness:oracle=OracleMock  KashiPairHarness:masterContract=KashiPairHarness KashiPairHarness:whitelistedSwapper=WhitelistedSwapper KashiPairHarness:redSwapper=Swapper \
	--solc solc6.12 \
	--settings -copyLoopUnroll=4,-b=1,-ignoreViewFunctions,-enableStorageAnalysis=true,-assumeUnwindCond,-ciMode=true \
	--verify KashiPairHarness:spec/kashiPair.spec \
	--staging shelly/sushiPackingBworIssueRuns800 \
	--cache KashiPairHarness \
	--msg "KashiPairHarness "  \
