<?php
/**
 * Imports the generated Elementor layouts into WordPress.
 * Run with: wp eval-file import.php
 */

$build = '/var/lib/freelancer/projects/40717325/build';
$pages_json  = json_decode( file_get_contents( "$build/elementor_data.json" ), true );
$chrome_json = json_decode( file_get_contents( "$build/chrome_data.json" ), true );

if ( ! $pages_json || ! $chrome_json ) {
	WP_CLI::error( 'Could not read generated JSON.' );
}

/* ------------------------------------------------------------------ palette */

$system_colors = [
	[ '_id' => 'primary',   'title' => 'Primary',   'color' => '#3A5A78' ],
	[ '_id' => 'secondary', 'title' => 'Secondary', 'color' => '#1F2933' ],
	[ '_id' => 'text',      'title' => 'Text',      'color' => '#2B2B2B' ],
	[ '_id' => 'accent',    'title' => 'Accent',    'color' => '#E8B54D' ],
];
$custom_colors = [
	[ '_id' => 'background', 'title' => 'Background', 'color' => '#F5F4F0' ],
	[ '_id' => 'surface',    'title' => 'Surface',    'color' => '#FFFFFF' ],
	[ '_id' => 'muted',      'title' => 'Muted text', 'color' => '#6B7280' ],
];

// Client-chosen pairing (19-sep-2026): Urbanist for headings, Roboto for body.
$head_font = 'Urbanist';
$body_font = 'Roboto';

$system_typography = [
	[
		'_id' => 'primary', 'title' => 'Primary',
		'typography_typography'     => 'custom',
		'typography_font_family'    => $head_font,
		'typography_font_weight'    => '800',
		'typography_text_transform' => 'uppercase',
		'typography_line_height'    => [ 'unit' => 'em', 'size' => 1.05 ],
	],
	[
		'_id' => 'secondary', 'title' => 'Secondary',
		'typography_typography'  => 'custom',
		'typography_font_family' => $head_font,
		'typography_font_weight' => '700',
	],
	[
		'_id' => 'text', 'title' => 'Text',
		'typography_typography'  => 'custom',
		'typography_font_family' => $body_font,
		'typography_font_weight' => '400',
		'typography_font_size'   => [ 'unit' => 'px', 'size' => 17 ],
		'typography_line_height' => [ 'unit' => 'em', 'size' => 1.65 ],
	],
	[
		'_id' => 'accent', 'title' => 'Accent',
		'typography_typography'  => 'custom',
		'typography_font_family' => $body_font,
		'typography_font_weight' => '600',
	],
];

$kit_id = (int) get_option( 'elementor_active_kit' );
if ( ! $kit_id ) {
	WP_CLI::error( 'No active Elementor kit.' );
}

$kit_settings = get_post_meta( $kit_id, '_elementor_page_settings', true );
if ( ! is_array( $kit_settings ) ) {
	$kit_settings = [];
}
$kit_settings = array_merge( $kit_settings, [
	'system_colors'             => $system_colors,
	'custom_colors'             => $custom_colors,
	'system_typography'         => $system_typography,
	'container_width'           => [ 'unit' => 'px', 'size' => 1200 ],
	'space_between_widgets'     => [ 'unit' => 'px', 'size' => 22 ],
	'body_background_background' => 'classic',
	'body_background_color'     => '#F5F4F0',
	'button_border_radius'      => [ 'unit' => 'px', 'top' => '0', 'right' => '0',
	                                 'bottom' => '0', 'left' => '0', 'isLinked' => true ],
	'viewport_mobile'           => 767,
	'viewport_tablet'           => 1024,
	'link_normal_color'         => '#3A5A78',
	'link_hover_color'          => '#E8B54D',
] );
update_post_meta( $kit_id, '_elementor_page_settings', $kit_settings );
WP_CLI::log( "Kit #$kit_id: palette + typography written." );

/* -------------------------------------------------------------- page writer */

function ug_set_elementor( $post_id, $data ) {
	update_post_meta( $post_id, '_elementor_data', wp_slash( wp_json_encode( $data ) ) );
	update_post_meta( $post_id, '_elementor_edit_mode', 'builder' );
	update_post_meta( $post_id, '_elementor_version', ELEMENTOR_VERSION );
}

/**
 * Look a post up by slug *within one post type*.
 *
 * get_page_by_path() also matches attachments, which silently converted the
 * scorecard image into a page the first time this ran. Query explicitly.
 */
function ug_find_by_slug( $slug, $post_type ) {
	$found = get_posts( [
		'post_type'        => $post_type,
		'name'             => $slug,
		'numberposts'      => 1,
		'post_status'      => 'any',
		'suppress_filters' => false,
	] );
	return $found ? $found[0] : null;
}

function ug_upsert_page( $slug, $title, $data ) {
	$existing = ug_find_by_slug( $slug, 'page' );
	$args = [
		'post_title'   => $title,
		'post_name'    => $slug,
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => '',
	];
	if ( $existing ) {
		$args['ID'] = $existing->ID;
		$id = wp_update_post( $args );
	} else {
		$id = wp_insert_post( $args );
	}
	update_post_meta( $id, '_wp_page_template', 'elementor_header_footer' );
	ug_set_elementor( $id, $data );
	return $id;
}

/*
 * Attachments live in the same slug namespace as pages, so an image called
 * scorecard.jpg would otherwise claim /scorecard/ and push the real page to
 * /scorecard-2/. Move any colliding attachment out of the way first.
 */
foreach ( array_keys( $pages_json['pages'] ) as $slug ) {
	$clash = ug_find_by_slug( $slug, 'attachment' );
	if ( $clash ) {
		wp_update_post( [ 'ID' => $clash->ID, 'post_name' => $slug . '-image' ] );
		WP_CLI::log( "  freed slug '$slug' from attachment #{$clash->ID}" );
	}
}

$cf7 = get_posts( [ 'post_type' => 'wpcf7_contact_form', 'numberposts' => 1 ] );
$cf7_id = $cf7 ? $cf7[0]->ID : 0;

$page_ids = [];
foreach ( $pages_json['pages'] as $slug => $p ) {
	$raw = wp_json_encode( $p['data'] );
	$raw = str_replace( 'CF7ID', (string) $cf7_id, $raw );
	$data = json_decode( $raw, true );
	$page_ids[ $slug ] = ug_upsert_page( $slug, $p['title'], $data );
	WP_CLI::log( sprintf( '  page %-12s #%d', $slug, $page_ids[ $slug ] ) );
}

/* ------------------------------------------------------- reusable sections */

foreach ( $pages_json['sections'] as $slug => $s ) {
	$existing = ug_find_by_slug( $slug, 'elementor_library' );
	$args = [
		'post_title'  => $s['title'],
		'post_name'   => $slug,
		'post_status' => 'publish',
		'post_type'   => 'elementor_library',
	];
	if ( $existing ) {
		$args['ID'] = $existing->ID;
		$id = wp_update_post( $args );
	} else {
		$id = wp_insert_post( $args );
	}
	update_post_meta( $id, '_elementor_template_type', 'container' );
	wp_set_object_terms( $id, 'container', 'elementor_library', false );
	ug_set_elementor( $id, $s['data'] );
	WP_CLI::log( sprintf( '  template %-14s #%d', $slug, $id ) );
}

/* ----------------------------------------------------------- menu (needed
   before the header renders, the widget references it by slug) ------------- */

$menu_name = 'Main Menu';
$menu = wp_get_nav_menu_object( $menu_name );
if ( ! $menu ) {
	$menu_id = wp_create_nav_menu( $menu_name );
} else {
	$menu_id = $menu->term_id;
	foreach ( wp_get_nav_menu_items( $menu_id ) as $item ) {
		wp_delete_post( $item->ID, true );
	}
}
foreach ( [ 'play' => 'Play', 'design' => 'Design', 'about' => 'About',
            'contact' => 'Contact' ] as $slug => $label ) {
	wp_update_nav_menu_item( $menu_id, 0, [
		'menu-item-title'     => $label,
		'menu-item-object'    => 'page',
		'menu-item-object-id' => $page_ids[ $slug ],
		'menu-item-type'      => 'post_type',
		'menu-item-status'    => 'publish',
	] );
}
$locations = get_theme_mod( 'nav_menu_locations', [] );
$locations['menu-1'] = $menu_id;
set_theme_mod( 'nav_menu_locations', $locations );
WP_CLI::log( "Menu 'Main Menu' #$menu_id rebuilt with 4 items." );

/* ------------------------------------------------------- header and footer */

// HFE stores the template type as 'type_header' / 'type_footer' (see its admin
// metabox); the bare 'header' value never matches and the theme keeps its own.
foreach ( [ 'header' => 'Site Header', 'footer' => 'Site Footer' ] as $type => $title ) {
	$existing = ug_find_by_slug( "site-$type", 'elementor-hf' );
	$args = [
		'post_title'  => $title,
		'post_name'   => "site-$type",
		'post_status' => 'publish',
		'post_type'   => 'elementor-hf',
	];
	if ( $existing ) {
		$args['ID'] = $existing->ID;
		$id = wp_update_post( $args );
	} else {
		$id = wp_insert_post( $args );
	}
	update_post_meta( $id, 'ehf_template_type', "type_$type" );
	update_post_meta( $id, 'ehf_target_include_locations', [
		'rule'     => [ 'basic-global' ],
		'specific' => [],
	] );
	ug_set_elementor( $id, $chrome_json[ $type ] );
	WP_CLI::log( sprintf( '  %s template #%d', $type, $id ) );
}

/* --------------------------------------------------------- site-wide config */

update_option( 'show_on_front', 'page' );
update_option( 'page_on_front', $page_ids['home'] );
update_option( 'blogname', 'Structure Template' );
update_option( 'blogdescription', 'Elementor structural template' );
update_option( 'permalink_structure', '/%postname%/' );
flush_rewrite_rules( false );

// Elementor housekeeping: let the theme own the page frame, no default lightbox
// on placeholder images, and keep the improved CSS loading defaults.
update_option( 'elementor_disable_color_schemes', 'yes' );
update_option( 'elementor_disable_typography_schemes', 'yes' );
update_option( 'elementor_css_print_method', 'internal' );

\Elementor\Plugin::$instance->files_manager->clear_cache();

WP_CLI::success( 'Import complete.' );
