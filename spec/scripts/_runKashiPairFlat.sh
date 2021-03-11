certoraRun.py spec/harness/KashiPairHarnessNOLIQ.sol spec/harness/DummyERC20A.sol \
	spec/harness/DummyERC20B.sol spec/harness/Swapper.sol spec/harness/SimpleBentoBox.sol contracts/mocks/OracleMock.sol spec/harness/DummyWeth.sol \
	--link KashiPairHarnessNOLIQ:collateral=DummyERC20A KashiPairHarnessNOLIQ:asset=DummyERC20B KashiPairHarnessNOLIQ:bentoBox=SimpleBentoBox KashiPairHarnessNOLIQ:oracle=OracleMock  KashiPairHarnessNOLIQ:masterContract=KashiPairHarnessNOLIQ \
	--solc solc6.12 \
	--settings -copyLoopUnroll=4,-b=1,-ignoreViewFunctions,-enableStorageAnalysis=true,-assumeUnwindCond,-ciMode=true,-recursionEntryLimit=10 \
	--verify KashiPairHarnessNOLIQ:spec/kashiPair.spec \
	--solc_args "['--optimize', '--optimize-runs', '800']" \
	--rule totalAssetElasticLeBentoBoxBalanceOf \
	--staging or/havocInfo \
	--cache KashiPairHarnessNOLIQ \
	--msg "KashiPairHarnessNOLIQFlat "  \