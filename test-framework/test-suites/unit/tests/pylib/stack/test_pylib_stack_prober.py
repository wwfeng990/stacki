import pytest

import pathlib
import tempfile
import shutil

import stack.probepal as pal

# the format here is the name, version, release, arch, distro as stacki expects them,
# and then a dictionary which is a mapping of files found in the `files` test data
# path to where they should be found in a path to look like the ISO we're pretending
# to probe 
PALLET_DATA = [
	['stacki', '05.03.00.00_20190905_5e7b1ce', 'sles12', 'x86_64', 'sles', {'roll-stacki.xml': 'roll-stacki.xml'}],
	['tdc-infrastructure', '01.05.00.00', 'sles12sp3', 'x86_64', 'sles', {'roll-tdc-infrastructure.xml': 'roll-tdc-infrastructure.xml'}],
	['CentOS', '7.4', 'redhat7', 'x86_64', 'redhat', {
		'CentOS-7-x86_64-Everything-1708.iso.treeinfo': '.treeinfo',
		'CentOS-7-x86_64-Everything-1708.iso.discinfo': '.discinfo',
	}],
	['CentOS', '7.7', 'redhat7', 'x86_64', 'redhat', {
		'CentOS-7-x86_64-DVD-1908.iso.treeinfo': '.treeinfo',
		'CentOS-7-x86_64-DVD-1908.iso.discinfo': '.discinfo',
	}],
	['RHEL', '7.6', 'redhat7', 'x86_64', 'redhat', {'rhel-server-7.6-x86_64-dvd.iso.treeinfo': '.treeinfo'}],
	['RHEL-Supp', '7.6', 'redhat7', 'x86_64', 'redhat', {'supp-server-7.6-rhel-7-x86_64-dvd.iso.treeinfo': '.treeinfo'}],
	['RHEL', '8.0.0', 'redhat8', 'x86_64', 'redhat', {'rhel-8.0-x86_64-dvd.iso.treeinfo': '.treeinfo'}],
	['RHEL-Supp', '8.0.0', 'redhat8', 'x86_64', 'redhat', {'supp-supplementary-8.0-rhel-8-x86_64-dvd.iso.treeinfo': '.treeinfo'}],
	['Fedora', '30', 'fedora30', 'x86_64', 'redhat', {'Fedora-Server-dvd-x86_64-30-1.2.iso.treeinfo': '.treeinfo'}],
	['SLES', '11.3', '1.138', 'x86_64', 'sles', {'SLES-11-SP3-DVD-x86_64-GM-DVD1.iso.content': 'content'}],
	['SLE-SDK', '11.3', '1.69', 'x86_64', 'sles', {'SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso.content': 'content'}],
	['SLES', '12', 'sp3', 'x86_64', 'sles', {'SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso.content': 'content'}],
	['SLE-SDK', '12', 'sp2', 'x86_64', 'sles', {'SLE-12-SP2-SDK-DVD-x86_64-GM-DVD1.iso.content': 'content'}],
	['SLES', '15', 'sles15', 'x86_64', 'sles', {'SLE-15-Installer-DVD-x86_64-GM-DVD1.iso.treeinfo': '.treeinfo'}],
	['SUSE-Enterprise-Storage', '4', 'ses4', 'x86_64', 'sles', {'SUSE-Enterprise-Storage-4-DVD-x86_64-GM-DVD1.iso.content': 'content'}],
	['Ubuntu', '18.04.3', 'ubuntu18.04', 'x86_64', 'ubuntu', {'ubuntu-18.04.3-desktop-amd64.iso.disk.info': '.disk/info'}],
	['Ubuntu-Server', '18.04.3', 'ubuntu18.04', 'x86_64', 'ubuntu', {'ubuntu-18.04.3-live-server-amd64.iso.disk.info': '.disk/info'}],
	['Ubuntu', '19.04', 'ubuntu19.04', 'x86_64', 'ubuntu', {'ubuntu-19.04-desktop-amd64.iso.disk.info': '.disk/info'}],
	['Ubuntu-Server', '19.04', 'ubuntu19.04', 'x86_64', 'ubuntu', {'ubuntu-19.04-live-server-amd64.iso.disk.info': '.disk/info'}],
]

class TestProbepal:

	@pytest.mark.parametrize('name, version, release, arch, distro_family, filemap', PALLET_DATA)
	def test_prober(self, test_file, name, version, release, arch, distro_family, filemap):
		''' test that the sample PALLET_DATA is identified correctly. '''

		prober = pal.Prober()

		with tempfile.TemporaryDirectory() as paldir:
			for input_file, dest in filemap.items():
				pathlib.Path(f'{paldir}/{dest}').parent.mkdir(parents=True, exist_ok=True)
				shutil.copyfile(test_file(f'pallet_artifacts/{input_file}'), f'{paldir}/{dest}')
			pal_map = prober.find_pallets(paldir)
			assert pal_map[paldir] == [pal.PalletInfo(name, version, release, arch, distro_family, paldir)]

	def test_prober_multi_args(self, test_file):
		''' test that find_pallets can accept multiple paths and return multiple pallets '''
		paldirs = []
		palinfos = []

		*pallet_data, filemap = PALLET_DATA[0]
		paldir = tempfile.TemporaryDirectory()
		for input_file, dest in filemap.items():
			pathlib.Path(f'{paldir.name}/{dest}').parent.mkdir(parents=True, exist_ok=True)
			shutil.copyfile(test_file(f'pallet_artifacts/{input_file}'), f'{paldir.name}/{dest}')
		paldirs.append(paldir.name)
		palinfos.append([pal.PalletInfo(*pallet_data, paldir.name)])

		*pallet_data, filemap = PALLET_DATA[1]
		paldir2 = tempfile.TemporaryDirectory()
		for input_file, dest in filemap.items():
			pathlib.Path(f'{paldir2.name}/{dest}').parent.mkdir(parents=True, exist_ok=True)
			shutil.copyfile(test_file(f'pallet_artifacts/{input_file}'), f'{paldir2.name}/{dest}')
		paldirs.append(paldir2.name)
		palinfos.append([pal.PalletInfo(*pallet_data, paldir2.name)])

		prober = pal.Prober()
		pal_map = prober.find_pallets(*paldirs)
		assert sorted(pal_map.values()) == sorted(palinfos)

	def test_prober_jumbo_pallets(self, test_file):
		''' test that find_pallets can identify jumbo pallets '''
		paldir = tempfile.TemporaryDirectory()

		*pallet_data, filemap = PALLET_DATA[0]
		for input_file, dest in filemap.items():
			pathlib.Path(f'{paldir.name}/pallet1/{dest}').parent.mkdir(parents=True, exist_ok=True)
			shutil.copyfile(test_file(f'pallet_artifacts/{input_file}'), f'{paldir.name}/pallet1/{dest}')
		p1 = pal.PalletInfo(*pallet_data, f'{paldir.name}/pallet1')

		*pallet_data, filemap = PALLET_DATA[1]
		for input_file, dest in filemap.items():
			pathlib.Path(f'{paldir.name}/pallet2/{dest}').parent.mkdir(parents=True, exist_ok=True)
			shutil.copyfile(test_file(f'pallet_artifacts/{input_file}'), f'{paldir.name}/pallet2/{dest}')
		p2 = pal.PalletInfo(*pallet_data, f'{paldir.name}/pallet2' )

		prober = pal.Prober()
		pal_map = prober.find_pallets(paldir.name)
		assert sorted(*pal_map.values()) == sorted([p1, p2])

	def test_collect_probes(self):
		''' test that instantiating Prober finds at least the probes that stacki ships '''
		prober = pal.Prober()
		assert len(prober.probes) >= 5

	def test_find_no_pallets(self):
		with tempfile.TemporaryDirectory() as paldir:
			prober = pal.Prober()
			pal_map = prober.find_pallets(paldir)
			assert pal_map[paldir] == []

	def test_stupid_stuff(self):
		class T(pal.Probe):
			def __init__(self, desc='null'):
				super().__init__(desc=desc)
			def probe(self, _):
				pass

		fake = T()

		assert repr(fake) == 'T(weight=90)'
		assert str(fake) == 'T (supports null)'