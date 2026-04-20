package backEnd;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileLock;

public class Wallet {
    /**
     * The RandomAccessFile of the wallet file
     */
    private RandomAccessFile file;
    // private Lock lock = new ReentrantLock(); // lock to access shared resource

    /**
     * Creates a Wallet object
     *
     * A Wallet object interfaces with the wallet RandomAccessFile
     */
    public Wallet() throws Exception {
        this.file = new RandomAccessFile(new File("backEnd/wallet.txt"), "rw");
    }

    /**
     * Gets the wallet balance.
     *
     * @return The content of the wallet file as an integer
     */
    public int getBalance() throws IOException {
        int retValue = 0;
        // a read lock - for reading purpose, allow
        // multiple instances to read the value at
        // the same time but blocks the writers
        // lock.lock();
        FileLock fileLock = null;
        try {
            fileLock = this.file.getChannel().lock(0, Long.MAX_VALUE, true);
            this.file.seek(0);
            retValue = Integer.parseInt(this.file.readLine());
        } finally {
            if (fileLock != null)
                fileLock.release();
            // lock.unlock();
        }
        return retValue;
    }

    /**
     * Sets a new balance in the wallet
     *
     * @param newBalance new balance to write in the wallet
     */
    public void setBalance(int newBalance) throws Exception {
        this.file.setLength(0);
        String str = Integer.valueOf(newBalance).toString() + '\n';
        this.file.writeBytes(str);
    }

    /**
     * Check if it is safe to withdraw a number of credits
     * @param valueToWithdraw           credits to withdraw
     * @throws Exception
     */
    public boolean safeWithdraw(int valueToWithdraw) throws Exception {
        boolean ret = false;

        FileLock fileLock = null;
        try {
            fileLock = this.file.getChannel().lock(0, Long.MAX_VALUE, false);
            this.file.seek(0);
            int currentBalance = Integer.parseInt(this.file.readLine());
            if (currentBalance - valueToWithdraw >= 0){
                this.setBalance(currentBalance - valueToWithdraw);
                ret = true;
            }
        } finally {
            if (fileLock != null) fileLock.release();
        }

        return ret;
    }

    /**
     * Closes the RandomAccessFile in this.file
     */
    public void close() throws Exception {
        this.file.close();
    }
}
