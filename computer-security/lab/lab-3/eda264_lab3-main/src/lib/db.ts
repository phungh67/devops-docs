import Database from 'better-sqlite3';
import md5 from 'md5';

const db = new Database('db.db');
db.exec(
	'CREATE TABLE IF NOT EXISTS Table_Users (' +
		'UID Integer Primary Key Autoincrement, ' +
		'Username TEXT NOT NULL,                ' +
		'Password TEXT NOT NULL,                ' +
		'SID TEXT)'
);

db.exec(
	'CREATE TABLE IF NOT EXISTS Table_Comments (' +
		'UID Integer Primary Key Autoincrement, ' +
		'Timestamp TEXT NOT NULL,               ' +
		'User Integer NOT NULL,                 ' +
		'Html TEXT)'
);

export function checkUserPass(username: string, password: string): { UID: number, Error?: Error } {
	const hash = md5(password);
	const command =
		"SELECT UID FROM Table_Users WHERE Username='" + username + "' AND Password='" + hash + "'";
	try {
		const uid = db.prepare(command).get() as { UID: number };
		return uid;
	} catch (e) {
		return { UID: 0, Error: e as Error }
	}
}

export function getUserFromSessionID(sid: string): { Username: string, Error?: Error } {
	const command = "SELECT Username FROM Table_Users WHERE SID='" + sid + "'";
	try {
		const username = db.prepare(command).get() as { Username: string };
		return username;
	} catch (e) {
		return { Username: "", Error: e as Error };
	}
}

export function getUIDFromSessionID(sid: string): number {
	const command = "SELECT UID FROM Table_Users WHERE SID='" + sid + "'";
	const uid = db.prepare(command).get() as { UID: number };
	return uid.UID;
}

export function addUserSessionID(uid: number, sid: string): boolean {
	const command = "UPDATE Table_Users SET SID='" + sid + "' WHERE UID='" + uid + "'";
	try {
		db.prepare(command).run();
		return true;
	} catch {
		return false;
	}
}

export function addComment(sid: string, comment: string): { done: boolean, Error?: Error } {
	const uid = getUIDFromSessionID(sid);
	const day = new Date();
	const command =
		"INSERT INTO Table_Comments (Timestamp, User, Html) Values('" +
		day.toDateString() +
		"', '" +
		uid +
		"', '" +
		comment +
		"')";
	try {
		db.exec(command);
		return { done: true };
	} catch (e) {
		return { done: false, Error: e as Error };
	}
}

export function getComments(): [
	{ Timestamp: string; Username: string; Html: string }
] {
	const command =
		'SELECT Timestamp, Username, Html FROM ' +
		'Table_Comments INNER JOIN Table_Users ON ' +
		'Table_Comments.User=Table_Users.UID';
	const result = db.prepare(command).all() as [
		{ Timestamp: string; Username: string; Html: string }
	];
	return result;
}
