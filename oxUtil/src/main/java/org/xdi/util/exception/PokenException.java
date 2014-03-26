package org.xdi.util.exception;

public class PokenException extends Exception {

	private static final long serialVersionUID = -5416921979568687942L;

	public PokenException(Throwable root) {
		super(root);
	}

	public PokenException(String string, Throwable root) {
		super(string, root);
	}

	public PokenException(String s) {
		super(s);
	}
}
