package netP5;

import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;
import java.net.DatagramPacket;
import java.util.Vector;

/**
 * @invisible
 */
class NetPlug {

	protected boolean isEventMethod = false;

	protected Method _myEventMethod;

	protected String _myEventMethodName = "netEvent";

	protected boolean isStatusMethod = false;

	protected Method _myStatusMethod;

	protected String _myStatusMethodName = "netStatus";

	protected Class _myParentClass;

	protected Object _myParent;

	protected Vector _myNetListeners;

	protected boolean isNetListener;

	protected NetPlug(Object theObject) {
		_myParent = theObject;
		_myNetListeners = new Vector();
		checkMethod();
	}

	protected void invoke(final Object theObject, final Method theMethod,
			final Object[] theArgs) {
		try {
			theMethod.invoke(theObject, theArgs);
		} catch (IllegalArgumentException e) {
			e.printStackTrace();
		} catch (IllegalAccessException e) {
			e.printStackTrace();
		} catch (InvocationTargetException e) {
			System.out
					.println("NetP5 ClassCastException. parsing failed for NetMessage "
							+ e);
		}
	}

	protected void checkMethod() {
		try {
			checkEventMethod();
			checkStatusMethod();
		} catch (Exception e) {
		}
	}

	private boolean checkEventMethod() {
		_myParentClass = _myParent.getClass();
		if (_myEventMethodName != null) {
			try {
				_myEventMethod = _myParentClass.getDeclaredMethod(
						_myEventMethodName, new Class[] { NetMessage.class });
				isEventMethod = true;
				_myEventMethod.setAccessible(true);
				return true;
			} catch (SecurityException e1) {
				e1.printStackTrace();
			} catch (NoSuchMethodException e1) {
				System.out
						.println("### NOTE. no netEvent(NetMessage theMessage) method available.");
			}
		}
		if (_myEventMethod != null) {
			return true;
		}
		return false;
	}

	private boolean checkStatusMethod() {
		_myParentClass = _myParent.getClass();
		if (_myStatusMethodName != null) {
			try {
				_myStatusMethod = _myParentClass.getDeclaredMethod(
						_myStatusMethodName, new Class[] { NetStatus.class });
				isStatusMethod = true;
				_myStatusMethod.setAccessible(true);
				return true;
			} catch (SecurityException e1) {
				e1.printStackTrace();
			} catch (NoSuchMethodException e1) {
				// System.out.println("### NOTE. no netStatus(NetStatus
				// theMessage) method available.");
			}
		}
		if (_myStatusMethod != null) {
			return true;
		}
		return false;
	}

	/**
	 * 
	 * @param theDatagramPacket
	 *            DatagramPacket
	 * @param thePort
	 *            int
	 * @invisible
	 */
	public void process(final DatagramPacket theDatagramPacket,
			final int thePort) {
		if (isNetListener || isEventMethod) {
			NetMessage n = new NetMessage(theDatagramPacket);
			for (int i = 0; i < _myNetListeners.size(); i++) {
				getListener(i).netEvent(n);
			}
			if (isEventMethod) {
				try {
					invoke(_myParent, _myEventMethod, new Object[] { n });
				} catch (ClassCastException e) {
					System.out
							.println("ChatP5.callMessage ClassCastException. failed to forward ChatMessage.");
				}
			}
		}
	}

	/**
	 * @invisible
	 * @param theIndex
	 */
	public void status(int theIndex) {
		if (isNetListener || isEventMethod) {
			NetStatus n = new NetStatus(theIndex);
			for (int i = 0; i < _myNetListeners.size(); i++) {
				getListener(i).netStatus(n);
			}
			if (isStatusMethod) {
				try {
					invoke(_myParent, _myStatusMethod, new Object[] { n });
				} catch (ClassCastException e) {
					System.out
							.println("ChatP5.callMessage ClassCastException. failed to forward ChatMessage.");
				}
			}
		}
	}

	/**
	 * 
	 * @param theTcpPacket
	 *            TcpPacket
	 * @param thePort
	 *            int
	 * @invisible
	 */
	public void process(final TcpPacket theTcpPacket, final int thePort) {

		if (isNetListener || isEventMethod) {
			NetMessage n = new NetMessage(theTcpPacket);
			for (int i = 0; i < _myNetListeners.size(); i++) {
				getListener(i).netEvent(n);
			}

			if (isEventMethod) {
				try {
					invoke(_myParent, _myEventMethod, new Object[] { n });
				} catch (ClassCastException e) {
					System.out
							.println("NetP5.callMessage ClassCastException. failed to forward ChatMessage.");
				}
			}
		}
	}

	protected void addListener(NetListener theListener) {
		_myNetListeners.add(theListener);
		isNetListener = true;
	}

	protected void removeListener(NetListener theListener) {
		_myNetListeners.remove(theListener);
		isNetListener = (_myNetListeners.size() > 0) ? true : false;
	}

	protected NetListener getListener(int theIndex) {
		return ((NetListener) _myNetListeners.get(theIndex));
	}

	protected Vector getListeners() {
		return _myNetListeners;
	}

}
