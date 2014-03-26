package org.xdi.util;

import java.lang.reflect.Array;
import java.util.Arrays;

/**
 * Utility methods to help work with arrays
 * 
 * @author Yuriy Movchan Date: 10.21.2010
 * @see org.apache.commons.lang.ArrayUtils
 */
public final class ArrayHelper {

	private ArrayHelper() {
	}

	@SuppressWarnings("unchecked")
	public static <T> T[] arrayMerge(T[]... arrays) {
		// Determine required size of new array
		int count = 0;
		for (T[] array : arrays) {
			count += array.length;
		}

		if (count == 0) {
			return (T[]) Array.newInstance(arrays.getClass().getComponentType().getComponentType(), 0);
		}

		// create new array of required class
		T[] mergedArray = (T[]) Array.newInstance(arrays[0][0].getClass(), count);

		// Merge each array into new array
		int start = 0;
		for (T[] array : arrays) {
			System.arraycopy(array, 0, mergedArray, start, array.length);
			start += array.length;
		}

		return (T[]) mergedArray;
	}

	public static <T> boolean isEmpty(T[] objects) {
		return (objects == null) || (objects.length == 0);
	}

	public static <T> boolean isNotEmpty(T[] objects) {
		return (objects != null) && (objects.length > 0);
	}

	@SuppressWarnings("unchecked")
	public static <T> T[] arrayClone(T[] array) {
		if (array == null) {
			return array;
		}
		if (array.length == 0) {
			return (T[]) Array.newInstance(array.getClass().getComponentType(), 0);
		}

		T[] clonedArray = (T[]) Array.newInstance(array[0].getClass(), array.length);
		System.arraycopy(array, 0, clonedArray, 0, array.length);

		return clonedArray;
	}

	public static String[] sortAndClone(String[] array) {
		if (array == null) {
			return array;
		}

		String[] clonedArray = arrayClone(array);
		Arrays.sort(clonedArray);

		return clonedArray;
	}

	public static boolean equalsIgnoreOrder(String[] values1, String[] values2) {
		String[] valuesSorted1 = sortAndClone(values1);
		String[] valuesSorted2 = sortAndClone(values2);

		return Arrays.equals(valuesSorted1, valuesSorted2);
	}

}
