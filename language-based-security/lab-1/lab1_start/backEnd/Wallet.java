package backEnd;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileLock;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Wallet {
    /**
     * The RandomAccessFile of the wallet file
     */  
    private RandomAccessFile file;
    private Lock lock = new ReentrantLock(); // lock to access shared resource

    /**
     * Creates a Wallet object
     *
     * A Wallet object interfaces with the wallet RandomAccessFile
     */
    public Wallet () throws Exception {
	this.file = new RandomAccessFile(new File("backEnd/wallet.txt"), "rw");
    }

    /**
     * Gets the wallet balance. 
     *
     * @return                   The content of the wallet file as an integer
     */
    public int getBalance() throws IOException {
        int retValue = 0;
        lock.lock();
        try {
            this.file.seek(0);
            retValue = Integer.parseInt(this.file.readLine());
        } finally {
            lock.unlock();
        }
	    return retValue;
    }

    /**
     * Sets a new balance in the wallet
     *
     * @param  newBalance          new balance to write in the wallet
     */
    public void setBalance(int newBalance) throws Exception {
        lock.lock();
        try {
	        this.file.setLength(0);
	        String str = Integer.valueOf(newBalance).toString()+'\n'; 
	        this.file.writeBytes(str); 
        } finally {
            lock.unlock();
        }
    }

    /**
     * Deduce a number of credits in the wallet
     * @param valueToWithdraw
     * @return 
     * @throws Exception
     */
    public void withDraw(int valueToWithdraw) throws Exception {
        lock.lock();
        FileLock fileLock = null;
        try {
            fileLock = this.file.getChannel().lock();
            int currentBalance = this.getBalance();
            if (!safeWithdraw(valueToWithdraw)){
                throw new IllegalArgumentException("Insufficient funds.");
            }
            this.file.setLength(0);
	        String str = Integer.valueOf(currentBalance - valueToWithdraw).toString()+'\n'; 
	        this.file.writeBytes(str); 
        } finally {
            if (fileLock != null) fileLock.release();
            lock.unlock();
        }
    }

    /**
     * Check if it is safe to withdraw a number of credits
     * @param valueToWithdraw           credits to withdraw
     * @throws Exception
     */
    public boolean safeWithdraw(int valueToWithdraw) throws Exception {
        int currentBalance = this.getBalance();
        return currentBalance - valueToWithdraw >= 0;
    }



    /**
     * Closes the RandomAccessFile in this.file
     */
    public void close() throws Exception {
	this.file.close();
    }
}
