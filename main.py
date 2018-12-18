from index import InvertedIndex
from SearchEngineGUI import SearchEngineGUI

if __name__ == '__main__':
	try:
		index = InvertedIndex()

		build_index = raw_input('Would you like to build database (y or n): ').lower()

		if build_index == 'y':
			index.create_index()
			index.compute_TfIdf()
			index.storeInDB()
		else:
			gui = SearchEngineGUI(index)

	except Exception as e:
		print(str(e))

	finally:
		index.close_connection()