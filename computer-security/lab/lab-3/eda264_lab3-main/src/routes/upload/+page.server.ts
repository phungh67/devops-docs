import { json, error, redirect } from '@sveltejs/kit';
import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import path from 'path';

import {
	getUserFromSessionID
} from '$lib/db';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
	const sessionid = cookies.get('sessionid');
	if (sessionid === undefined) redirect(307, '/');
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
		redirect(307, '/');
	}
}
/** @type {import('./$types').Actions} */
export const actions = {
	upload: async ({ request }) => {
		const data = await request.formData();
		const formData = Object.fromEntries(data);

		if (
			!(formData.fileToUpload as File).name ||
			(formData.fileToUpload as File).name === 'undefined'
		) {
			return { sucess: false, message: 'You must provide a file to upload' };
		}

		const p = data.get('path');
		const { fileToUpload } = formData as { fileToUpload: File };
		var uploadPath;
		if (p !== undefined && p !== '') {
			uploadPath = `uploads/${p}${path.extname(fileToUpload.name)}`;
		} else {
			uploadPath = `uploads/${fileToUpload.name}`;
		}

		if (!existsSync(path.dirname(`static/${uploadPath}`))) {
			mkdirSync(path.dirname(`static/${uploadPath}`), { recursive: true });
		}

		writeFileSync(`static/${uploadPath}`, Buffer.from(await fileToUpload.arrayBuffer()));

		return { success: true, path: uploadPath };
	}
};
