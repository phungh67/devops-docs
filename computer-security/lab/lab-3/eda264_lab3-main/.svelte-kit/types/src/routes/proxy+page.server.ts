// @ts-nocheck
import { json, error } from '@sveltejs/kit';

import {
	addUserSessionID,
	checkUserPass,
	getUIDFromSessionID,
	getUserFromSessionID
} from '$lib/db';

/** @param {Parameters<import('./$types').PageServerLoad>[0]} event */
export async function load({ cookies }) {
	const sessionid = cookies.get('sessionid');
	if (sessionid === undefined) return {};
	const user = getUserFromSessionID(sessionid);
	if (user !== undefined) {
		if (user.Error === undefined)
			return { user, sessionid };
		else {
			cookies.delete('sessionid', { path: '/' });
			error(500, user.Error.message)
		}
	} else {
		cookies.delete('sessionid', { path: '/' });
		return {};
	}
}

/** */
export const actions = {
	login:/** @param {import('./$types').RequestEvent} event */  async ({ cookies, request }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');

		const isValidUser = checkUserPass(username, password);

		if (isValidUser !== undefined) {
			if (isValidUser.Error === undefined) {
				let uuid = crypto.randomUUID();
				cookies.set('sessionid', uuid, { httpOnly: false, path: '/' });
				addUserSessionID(isValidUser.UID, uuid);
				return { success: true };
			} else
				error(500, isValidUser.Error.message)
		} else {
			return { success: false };
		}
	},

	logout:/** @param {import('./$types').RequestEvent} event */  async ({ cookies }) => {
		const sid = cookies.get('sessionid');
		const uid = getUIDFromSessionID(sid);
		addUserSessionID(uid, '-1');
		cookies.delete('sessionid', { path: '/' });
	}
};
