import unittest
from rdkit import Chem
from rdkit.Chem import AllChem
import os
from swiftpol import build 
from rdkit.Chem.Descriptors import ExactMolWt
from openff.toolkit.topology import Molecule
import numpy as np  # Added for numpy array type checking
from openff.toolkit.topology import Topology  # Added for topology type checking
import warnings
warnings.filterwarnings("ignore")

# Define all test cases

class TestBuildPLGARing(unittest.TestCase):
    def test_build_PLGA_ring(self):
        sequence = 'LLGG'
        reaction = AllChem.ReactionFromSmarts('[I:1][O:2].[I:3][C:4]>>[C:4][O:2].[I:3][I:1]')
        terminal = 'hydroxyl'
        polymer, LA_ratio, GA_ratio = build.build_PLGA_ring(sequence, reaction, terminal)
        
        # Check if the returned polymer is a RDKit Mol object
        self.assertTrue(isinstance(polymer, Chem.rdchem.Mol))
        
        # Check if the returned ratios are as expected
        self.assertEqual(LA_ratio, 50.0)
        self.assertEqual(GA_ratio, 50.0)

class TestBuildLinearCopolymer(unittest.TestCase):
    def test_build_linear_copolymer(self):
        sequence = 'ABAB'
        monomer_a_smiles = 'OC(=O)CO'
        monomer_b_smiles = 'C[C@@H](C(=O)[OH])O'
        reaction = AllChem.ReactionFromSmarts('[C:1][HO:2].[HO:3][C:4]>>[C:1][O:2][C:4].[O:3]')
        polymer, A_ratio, B_ratio = build.build_linear_copolymer(sequence, monomer_a_smiles, monomer_b_smiles, reaction)
        
        # Check if the returned polymer is a RDKit Mol object
        self.assertTrue(isinstance(polymer, Chem.rdchem.Mol))
        
        # Check if the returned ratios are as expected
        self.assertEqual(A_ratio, 50.0)
        self.assertEqual(B_ratio, 50.0)

class TestPDI(unittest.TestCase):
    def test_PDI(self):
        # Create some RDKit molecule objects
        mol1 = Chem.MolFromSmiles('CC(=O)O')
        mol2 = Chem.MolFromSmiles('CC(=O)OC')
        mol3 = Chem.MolFromSmiles('CC(=O)OC')
        
        chains = [mol1, mol2, mol3]
        
        pdi, mn, mw = build.PDI(chains)
        
        # Check if the returned PDI, Mn, and Mw are floats
        self.assertTrue(isinstance(pdi, float))
        self.assertTrue(isinstance(mn, float))
        self.assertTrue(isinstance(mw, float))

        # Check if the returned PDI, Mn, and Mw are as expected
        self.assertAlmostEqual(pdi, 1.77, places=2)
        self.assertAlmostEqual(mn, 69.3, places=1)
        self.assertAlmostEqual(mw, 122.6, places=1)

class TestBlockinessCalc(unittest.TestCase):
    def test_blockiness_calc(self):
        sequence = 'GLGLGLGL'
        blockiness, block_length_G, block_length_L = build.blockiness_calc(sequence)
        
        # Check if the returned blockiness is float
        self.assertTrue(isinstance(blockiness, float))


        # Check if the returned blockiness, block_length_G, and block_length_L are as expected
        self.assertAlmostEqual(blockiness, 0.0, places=2)
        self.assertAlmostEqual(block_length_G, 1.0, places=2)
        self.assertAlmostEqual(block_length_L, 1.0, places=2)
        
        #Test case - PLA sequence
        sequence_L = 'LLLLLLLL'
        blockiness_L, block_length_G_2, block_length_L_2 = build.blockiness_calc(sequence_L)
        self.assertTrue(isinstance(blockiness_L, str))

#PLGA build test
class TestPLGABuild(unittest.TestCase):
    def test_plga_build(self):
        x = build.PLGA_system(80, 10, 1.0, 'ester', 5)
        
        self.assertTrue(len(x.chains)==5)
        self.assertTrue(72 <= round(x.lactide_actual) <= 88)
        self.assertTrue(9 <= round(x.max_length)<= 11)
        self.assertTrue(1.5 <= round(x.PDI) <= 5)
        print(x.PDI)
        self.assertTrue(x.mean_blockiness==1)
        
        x.generate_conformers()
        self.assertTrue(len(x.chains[0].conformers[0])==len(x.chains[0].atoms))
        x.charge_system()
        self.assertTrue(len(x.chains[0].partial_charges)==len(x.chains[0].atoms))
        from openff.units import unit
        solv_system = x.solvate_system(resid_monomer = 0.5, salt_concentration = 0.1 * unit.mole / unit.liter)
        self.assertTrue(x.residual_monomer==0.5)
        
#Test calculate box components
class TestCalculateBoxComponents(unittest.TestCase):
    def test_calculate_box_components(self):
        # Create a PLGA system
        x = build.PLGA_system(75, 30, 1.7, 'ester', 2)
        x.generate_conformers()
        # Calculate box components
        molecules, number_of_copies, topology, box_vectors = build.calculate_box_components(chains = x.chains,
                                                                                            sequence=x.sequence)        

        # Check if the returned molecules is a list
        self.assertTrue(isinstance(molecules, list))
        self.assertEqual(len(molecules), 5)
        # Check if the returned number_of_copies is an integer
        self.assertTrue(isinstance(number_of_copies, list))
        print(number_of_copies)
        # Check if the returned topology is a Topology object
        self.assertTrue(isinstance(topology, Topology))
        # Check if the returned box_vectors has the correct shape
        self.assertEqual(box_vectors.shape, (3, 3))        

        
        
        
        

# Run

if __name__ == '__main__':
    unittest.main()
