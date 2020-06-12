# privateMCgeneration
scripts for full chain CMS private MC generation

1. Create LHE-GEN step samples with MCLHEgenerationAutomatization.py
2. Create from GENSIM samples Premix step1 samples with MCgenerationAODSingleTop.py or one of its derivates numbered with 1,2,3,4.
3. Create from Premix step 1 samples AOD samples with MCgenerationAODSingleTopCheck_step2.py or one of its derivatie scripts MCgenerationAODSingleTop*_step2.py
4. Create AOD samples MiniAOD ones with MCgenerationMiniAODSingleTop.py

Attention! For accessing pileup root files stored on another Tier storage location or uploading to /pnfs you need a valid proxy.
